import { useState } from "react";
import FileUpload from "./components/FileUpload";

export default function App() {
  const [action, setAction] = useState("preprocess");
  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Structura – Data Tool</h1>
      <div className="mb-6 flex space-x-4">
        <button
          className={`px-4 py-2 rounded-xl ${action==="preprocess"?"bg-blue-500 text-white":"bg-gray-200"}`}
          onClick={()=>setAction("preprocess")}
        >
          Preprocess
        </button>
        <button
          className={`px-4 py-2 rounded-xl ${action==="convert"?"bg-blue-500 text-white":"bg-gray-200"}`}
          onClick={()=>setAction("convert")}
        >
          Convert to Structured
        </button>
      </div>
      <FileUpload action={action} />
    </div>
  );
}
