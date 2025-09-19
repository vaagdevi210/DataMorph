from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io, re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
        .str.title()
    )
    return df

def fill_missing(df: pd.DataFrame, method: str, value: str = None) -> pd.DataFrame:
    if method == "mean":
        return df.fillna(df.mean(numeric_only=True))
    if method == "value" and value is not None:
        return df.fillna(value)
    if method == "drop":
        return df.dropna()
    return df

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    action: str = Form(...),
    missing: str = Form("none"),
    fill_value: str = Form(None),
    split_col: str = Form(None),
    join_cols: str = Form(None)
):
    try:
        contents = await file.read()
        ext = file.filename.split(".")[-1].lower()
        if ext not in ["csv", "xlsx"]:
            raise HTTPException(status_code=400, detail="Only CSV/XLSX allowed")

        df = pd.read_excel(io.BytesIO(contents)) if ext == "xlsx" \
             else pd.read_csv(io.BytesIO(contents), encoding_errors="ignore")

        if action == "preprocess":
            df = clean_column_names(df)
            if missing != "none":
                df = fill_missing(df, missing, fill_value)
            df.drop_duplicates(inplace=True)
            if split_col and split_col in df.columns:
                splits = df[split_col].str.split(" ", n=1, expand=True)
                df[split_col + "_1"] = splits[0]
                df[split_col + "_2"] = splits[1]
            if join_cols:
                cols = [c.strip() for c in join_cols.split(",") if c.strip() in df.columns]
                if cols:
                    df["_Joined"] = df[cols].astype(str).agg(" ".join, axis=1)

        elif action == "convert":
            df = clean_column_names(df)
            # placeholder: simple flattening logic
            # add more sophisticated structuring as needed
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        out_stream = io.BytesIO()
        df.to_csv(out_stream, index=False)
        out_stream.seek(0)
        return StreamingResponse(
            out_stream,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=processed.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
