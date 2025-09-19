from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io, tempfile, os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_read(upload: UploadFile) -> pd.DataFrame:
    data = upload.file.read()
    name = upload.filename.lower()
    try:
        if name.endswith(".csv"):
            try:
                return pd.read_csv(io.BytesIO(data))
            except UnicodeDecodeError:
                # fallback if encoding issues
                return pd.read_csv(io.BytesIO(data), encoding="latin1")
        elif name.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(data))
        else:
            raise HTTPException(status_code=400, detail="Only CSV/XLSX accepted")
    finally:
        upload.file.close()

@app.post("/process")
async def process_dataset(
    file: UploadFile = File(...),
    mode: str = Form(...),   # 'preprocess' | 'structure'
    options: str = Form("{}") # JSON string of preprocessing choices
):
    df = safe_read(file)

    if mode == "preprocess":
        opts = json.loads(options)

        # ---- Column name handling ----
        if opts.get("strip_col_whitespace"):
            df.columns = [c.strip() for c in df.columns]
        if opts.get("capitalize_cols"):
            df.columns = [c.strip().capitalize() for c in df.columns]
        if opts.get("lower_cols"):
            df.columns = [c.strip().lower() for c in df.columns]

        # ---- Rename by map or regex remove ----
        rename_map = opts.get("rename_map")
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
        remove_expr = opts.get("remove_expr")
        if remove_expr:
            import re
            df.columns = [re.sub(remove_expr, "", c) for c in df.columns]

        # ---- String whitespace strip ----
        if opts.get("strip_cell_whitespace"):
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # ---- Missing data ----
        miss = opts.get("missing")
        if miss:
            if miss["method"] == "drop":
                df = df.dropna()
            elif miss["method"] == "fill_const":
                df = df.fillna(miss.get("value", ""))
            elif miss["method"] == "fill_mean":
                df = df.fillna(df.mean(numeric_only=True))

        # ---- Duplicates ----
        if opts.get("remove_duplicates"):
            df = df.drop_duplicates()

        # ---- Split column ----
        split_info = opts.get("split_column")
        if split_info:
            col, sep, new_cols = split_info["col"], split_info["sep"], split_info["new_cols"]
            splits = df[col].astype(str).str.split(sep, expand=True)
            for i, n in enumerate(new_cols):
                df[n] = splits[i]
            df.drop(columns=[col], inplace=True)

        # ---- Join columns ----
        join_info = opts.get("join_columns")
        if join_info:
            cols, sep, new_col = join_info["cols"], join_info["sep"], join_info["new_col"]
            df[new_col] = df[cols].astype(str).agg(sep.join, axis=1)
            df.drop(columns=cols, inplace=True)

    elif mode == "structure":
        # Simple example: flatten JSON-like text columns
        for c in df.columns:
            if df[c].astype(str).str.startswith("{").any():
                expanded = pd.json_normalize(df[c].dropna().apply(eval))
                df = df.drop(columns=[c]).join(expanded, rsuffix=f"_{c}")
    else:
        raise HTTPException(status_code=400, detail="Unknown mode")

    # Output format matches input
    ext = ".csv" if file.filename.lower().endswith(".csv") else ".xlsx"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    if ext == ".csv":
        df.to_csv(tmp.name, index=False)
    else:
        df.to_excel(tmp.name, index=False)

    return FileResponse(
        tmp.name,
        filename=f"converted_{file.filename}",
        background=lambda: os.unlink(tmp.name),
        media_type="text/csv" if ext==".csv"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
