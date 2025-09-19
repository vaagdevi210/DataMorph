import { useState } from "react";

export default function FileUpload({ action }) {
  const [file, setFile] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    form.append("action", action);
    form.append("missing", "mean"); // example: could be dynamic

    setDownloading(true);
    const res = await fetch("http://localhost:8000/process", {
      method: "POST",
      body: form
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "processed.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setDownloading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md w-full max-w-md">
      <input
        type="file"
        accept=".csv,.xlsx"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />
      <button
        disabled={!file || downloading}
        className="w-full px-4 py-2 bg-green-500 text-white rounded-xl"
      >
        {downloading ? "Processing..." : "Upload & Download"}
      </button>
    </form>
  );
}
