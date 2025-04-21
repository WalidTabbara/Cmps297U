import React, { useState, useRef } from "react";
import axios from "axios";
import Latex from "react-latex";
import "katex/dist/katex.min.css";
import "./App.css";

// First‑order method options
const firstOrderMethods = {
  "1": [
    "Separable",
    "Linear",
    "Exact / Integrating Factor / Homogeneous",
    "Bernoulli",
    "Reduction to Separation of Variables",
  ],
};

// Second‑order method options
const secondOrderMethods = {
  Homogeneous: [
    "Homogeneous - Reduction of Order",
    "Homogeneous - Constant Coefficients",
    "Homogeneous - Cauchy-Euler",
  ],
  "Non-Homogeneous": [
    "Non-Homogeneous - Constant Coefficients",
    "Non-Homogeneous - Cauchy-Euler",
    "Non-Homogeneous - Variation of Parameters",
  ],
};

// Instruction notes for each method
const methodInstructions = {
  Separable: "Input must be of the form dy/dx = f(x)*g(y).",
  Linear:
    "Input must be of the form a(x) dy/dx + b(x)y = c(x), where a(x) ≠ 0.",
  "Exact / Integrating Factor / Homogeneous":
    "Input must be of the form M(x, y) dx + N(x, y) dy = 0.",
  Bernoulli:
    "Input must be of the form a(x) dy/dx + b(x)y = c(x)yⁿ, where n ≠ 0 and n ≠ 1.",
  "Reduction to Separation of Variables":
    "Input must be of the form dy/dx = f(Ax+By+C).",
  "Homogeneous - Reduction of Order":
    "Enter a(x), b(x), c(x), and y₁(x) where y₁ is the first linearly independent solution.",
  "Homogeneous - Constant Coefficients":
    "Enter a, b, c for ay'' + by' + cy = 0.",
  "Homogeneous - Cauchy-Euler":
    "Enter a, b, c for ax²y'' + bxy' + cy = 0.",
  "Non-Homogeneous - Constant Coefficients":
    "Enter a, b, c, and the right-hand side f(x) for ay'' + by' + cy = f(x).",
  "Non-Homogeneous - Cauchy-Euler":
    "Enter a, b, c, and the right-hand side f(x) for ax²y'' + bxy' + cy = f(x).",
  "Non-Homogeneous - Variation of Parameters":
    "Enter a(x), b(x), c(x), y₁(x), and y₂(x) where y₁ and y₂ are the linearly independent solutions of the homogeneous equation a(x)y'' + b(x)y' + c(x)y = 0 and f(x) is the right hand side.",
};

function App() {
  // ─── Core solver state ───
  const [order, setOrder] = useState("");
  const [method, setMethod] = useState("");
  const [secondCategory, setSecondCategory] = useState("");
  const [output, setOutput] = useState("");

  // ─── First‑order inputs ───
  const [equation, setEquation] = useState("");
  const [sepFx, setSepFx] = useState("");
  const [sepGy, setSepGy] = useState("");
  const [aVal, setAVal] = useState("");
  const [bVal, setBVal] = useState("");
  const [cVal, setCVal] = useState("");
  const [Mxy, setMxy] = useState("");
  const [Nxy, setNxy] = useState("");
  const [nVal, setNVal] = useState("");
  // For Reduction to Separation
  const [sepFunc, setSepFunc] = useState("");

  // ─── Second‑order inputs ───
  const [y1Val, setY1Val] = useState("");
  const [y2Val, setY2Val] = useState("");
  const [fVal, setFVal] = useState("");

  // ─── PDF upload & retrieval state ───
  const [selectedPDF, setSelectedPDF] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [pdfList, setPdfList] = useState([]);
  const [isLoadingPDFs, setIsLoadingPDFs] = useState(false);

  // ─── Random‑ODE generation state ───
  const [generatedODE, setGeneratedODE] = useState("");
  const [isGeneratingODE, setIsGeneratingODE] = useState(false);
  const [generateError, setGenerateError] = useState("");

  
  // show/hide the PDF‑list modal
  const [showPdfPanel, setShowPdfPanel] = useState(false);
  // show/hide the Generated‑ODE modal
  const [showGeneratedPanel, setShowGeneratedPanel] = useState(false);

  // show/hide the Instructions modal
  const [showInstructions, setShowInstructions] = useState(false);

  // panel controls for the new email features
  const [showSubscribePanel,   setShowSubscribePanel]   = useState(false);
  const [showUnsubscribePanel, setShowUnsubscribePanel] = useState(false);
  const [showFetchPanel,       setShowFetchPanel]       = useState(false);

  

  // ─── History state ───
  const [historyRecords, setHistoryRecords] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

   // subscribe to Learning Companion (add to email list) post: https://n7wj0oyecg.execute-api.eu-west-1.amazonaws.com/subscribe
   const [subscriberEmail, setSubscriberEmail] = useState("");
   const [subscribeStatus, setSubscribeStatus] = useState("");
   // list emails (display subscribers) get: https://36mckc3nx1.execute-api.eu-west-1.amazonaws.com/emails
   const [emailList, setEmailList] = useState([]);
   const [emailListStatus, setEmailListStatus] = useState("");

   // controls the Unsubscribe modal
  const [showUnsubscribeModal, setShowUnsubscribeModal] = useState(false);


  // ─── Refs ───
  const equationRef = useRef(null);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // ─── Handler: select & upload PDF immediately ───
  const handlePDFSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSelectedPDF(file);
    await handlePDFUpload();
  };

  // ─── Handler: Upload selected PDF ───
  const handlePDFUpload = async () => {
    if (!selectedPDF) {
      setUploadStatus("Please select a PDF file first.");
      return;
    }
    try {
      const buffer = await selectedPDF.arrayBuffer();
      await axios.post(
        "https://6k3rznj86l.execute-api.eu-west-1.amazonaws.com/dev/upload",
        buffer,
        { headers: { "Content-Type": "application/pdf" } }
      );
      setUploadStatus("✅ Upload successful!");
    } catch (err) {
      console.error(err);
      setUploadStatus(
        err.response
          ? `❌ Upload failed: ${err.response.status} ${err.response.statusText}`
          : "❌ Upload failed."
      );
    }
  };

  // ─── Handler: Retrieve uploaded PDFs and show panel ───
const fetchUploadedPDFs = async () => {
  setIsLoadingPDFs(true);
  try {
    const res = await axios.get(
      "https://q947q5arne.execute-api.eu-west-1.amazonaws.com/dev/get"
    );
    const body =
      typeof res.data.body === "string"
        ? JSON.parse(res.data.body)
        : res.data.body;
    setPdfList(body.pdfs || []);
    setShowPdfPanel(true);    // open the PDF‑list modal
  } catch (err) {
    console.error(err);
    setPdfList([]);
  } finally {
    setIsLoadingPDFs(false);
  }
};

// ─── Handler: Generate a random ODE and show panel ───
const handleGenerateODE = async () => {
  setIsGeneratingODE(true);
  setGeneratedODE("");
  setGenerateError("");
  try {
    const res = await axios.get(
      "https://zmscb26zwl.execute-api.eu-west-1.amazonaws.com/dev/generate"
    );
    const raw = res.data.body || "";
    const clean = raw.replace(/\\\[|\\\]/g, "").trim();
    setGeneratedODE(clean);
    setEquation(clean);
    setShowGeneratedPanel(true);  // open the Generated‑ODE modal
  } catch (err) {
    console.error(err);
    setGenerateError("❌ Failed to generate ODE. Please try again.");
  } finally {
    setIsGeneratingODE(false);
  }
};
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const handleSubscribe = async () => {
  if (!subscriberEmail) {
    setSubscribeStatus("❌ Please enter a valid email.");
    return;
  }

  setSubscribeStatus("⏳ Subscribing...");

  try {
    const res = await fetch("https://n7wj0oyecg.execute-api.eu-west-1.amazonaws.com/subscribe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email: subscriberEmail })
    });

    const resultText = await res.text(); // Your Lambda returns plain text
    setSubscribeStatus("✅ " + resultText);
    setSubscriberEmail(""); // Clear field on success
  } catch (err) {
    console.error("Subscription error:", err);
    setSubscribeStatus("❌ Subscription failed. Try again.");
  }
};


// unsubscribe to Learning Companion (remove from email list) post: https://ho21nmnzd9.execute-api.eu-west-1.amazonaws.com/unsubscribe
const handleUnsubscribe = async () => {
  if (!subscriberEmail) {
    setSubscribeStatus("❌ Please enter your email to unsubscribe.");
    return;
  }

  setSubscribeStatus("⏳ Processing unsubscribe...");

  try {
    const res = await fetch("https://ho21nmnzd9.execute-api.eu-west-1.amazonaws.com/unsubscribe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email: subscriberEmail })
    });

    const resultText = await res.text();
    setSubscribeStatus("✅ " + resultText);
    setSubscriberEmail(""); // Optionally clear the field
  } catch (err) {
    console.error("Unsubscribe error:", err);
    setSubscribeStatus("❌ Unsubscribe failed. Try again.");
  }
};

const handleFetchEmails = async () => {
    setEmailListStatus("⏳ Fetching...");
    try {
      const res = await fetch("https://36mckc3nx1.execute-api.eu-west-1.amazonaws.com/emails");
      const data = await res.json();
      if (data.emails && Array.isArray(data.emails)) {
        setEmailList(data.emails);
        setEmailListStatus(`✅ Fetched ${data.emails.length} emails.`);
      } else {
        setEmailListStatus("❌ Unexpected response format.");
      }
    } catch (err) {
      console.error("Failed to fetch email list:", err);
      setEmailListStatus("❌ Failed to fetch emails.");
    }
  };
  

  // ─── Handler: Solve ODE ───
  const handleSolve = async () => {
    const payload = { x: "x", y: "y", order, method };
    if (order === "1") {
      if (method === "Separable") {
        payload.f = sepFx.trim();
        payload.g = sepGy.trim();
      } else if (method === "Linear") {
        payload.a = aVal.trim();
        payload.b = bVal.trim();
        payload.c = cVal.trim();
      } else if (method === "Exact / Integrating Factor / Homogeneous") {
        payload.M = Mxy.trim();
        payload.N = Nxy.trim();
      } else if (method === "Bernoulli") {
        payload.a = aVal.trim();
        payload.b = bVal.trim();
        payload.c = cVal.trim();
        payload.n = parseInt(nVal, 10);
      } else if (method === "Reduction to Separation of Variables") {
        payload.f = sepFunc.trim();
        payload.A = aVal.trim();
        payload.B = bVal.trim();
        payload.C = cVal.trim();
      }
    } else if (order === "2") {
      payload.a = aVal.trim();
      payload.b = bVal.trim();
      payload.c = cVal.trim();
    
      if (method === "Homogeneous - Reduction of Order") {
        payload.y1 = y1Val.trim();
      } else if (method === "Non-Homogeneous - Variation of Parameters") {
        payload.y1 = y1Val.trim();
        payload.y2 = y2Val.trim();
        payload.f  = fVal.trim();
      } else if (method.startsWith("Non-Homogeneous")) {
        // covers Constant Coeffs and Cauchy‑Euler non‑homogeneous
        payload.f = fVal.trim();
      }
    }
    try {
      const res = await axios.post("http://localhost:5000/solve", payload);
      setOutput(res.data.steps || "");
    } catch {
      setOutput("Error solving the equation. Check the input and try again.");
    }
  };

  // ─── Reset functions ───
  const newSeparableODE = () => {
    setSepFx(""); setSepGy(""); setOutput("");
  };
  const newFirstOrderODE = () => {
    setMethod(""); setEquation(""); setOutput("");
  };
  const newSecondOrderODE = () => {
    setSecondCategory(""); setMethod(""); setOutput("");
  };
  const newODE = () => {
    setOrder(""); setSecondCategory(""); setMethod("");
    setEquation(""); setSepFx(""); setSepGy("");
    setAVal(""); setBVal(""); setCVal("");
    setMxy(""); setNxy(""); setFVal("");
    setOutput("");
  };
  // Reset only the inputs for the currently selected method, then clear output
const newMethodODE = () => {
  setOutput("");
  if (order === "1") {
    switch (method) {
      case "Separable":
        setSepFx(""); setSepGy("");
        break;
      case "Linear":
        setAVal(""); setBVal(""); setCVal("");
        break;
      case "Exact / Integrating Factor / Homogeneous":
        setMxy(""); setNxy("");
        break;
      case "Bernoulli":
        setAVal(""); setBVal(""); setCVal(""); setNVal("");
        break;
      case "Reduction to Separation of Variables":
        setSepFunc(""); setAVal(""); setBVal(""); setCVal("");
        break;
      default:
        break;
    }
  } else if (order === "2") {
    switch (method) {
      case "Homogeneous - Reduction of Order":
        setAVal(""); setBVal(""); setCVal(""); setY1Val("");
        break;
      case "Homogeneous - Constant Coefficients":
      case "Homogeneous - Cauchy-Euler":
      case "Non-Homogeneous - Constant Coefficients":
      case "Non-Homogeneous - Cauchy-Euler":
        setAVal(""); setBVal(""); setCVal(""); setFVal("");
        break;
      case "Non-Homogeneous - Variation of Parameters":
        setAVal(""); setBVal(""); setCVal(""); setY1Val(""); setY2Val("");
        break;
      default:
        break;
    }
  }
};

  return (
    <div className="container">
      <h1 className="header">ODE Solver</h1>
  
      {/* Top‑Left Action Buttons */}
    <div className="topLeftActions">
      <button className="btn-upload" onClick={() => document.getElementById("pdfInput").click()}>
        Upload
      </button>
      <button className="btn-retrieve" onClick={fetchUploadedPDFs} disabled={isLoadingPDFs}>
        {isLoadingPDFs ? "Loading…" : "Retrieve"}
      </button>
      <button className="btn-generate" onClick={handleGenerateODE} disabled={isGeneratingODE}>
        {isGeneratingODE ? "Generating…" : "Generate Random ODE"}
      </button>
      <input
        id="pdfInput"
        type="file"
        accept="application/pdf"
        style={{ display: "none" }}
        onChange={handlePDFSelect}
      />
    </div>

      {/* ─── PDF LIST MODAL ─── */}
  {showPdfPanel && (
    <div className="modalOverlay" onClick={() => setShowPdfPanel(false)}>
      <div className="panel" onClick={e => e.stopPropagation()}>
        <button className="closeButton" onClick={() => setShowPdfPanel(false)}>
          &times;
        </button>
        <h3>Available PDFs</h3>
        {isLoadingPDFs ? (
          <p>Loading PDFs…</p>
        ) : pdfList.length > 0 ? (
          <ul>
            {pdfList.map((pdf, i) => (
              <li key={i}>
                <a href={pdf.url} target="_blank" rel="noopener noreferrer">
                  {pdf.filename}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p>No PDFs found.</p>
        )}
      </div>
    </div>
  )}

  {/* ─── GENERATED ODE MODAL ─── */}
  {showGeneratedPanel && (
    <div className="modalOverlay" onClick={() => setShowGeneratedPanel(false)}>
      <div className="panel" onClick={e => e.stopPropagation()}>
        <button
          className="closeButton"
          onClick={() => setShowGeneratedPanel(false)}
        >
          &times;
        </button>
        <h3>Generated ODE</h3>
        <Latex>{generatedODE}</Latex>
      </div>
    </div>
  )}

  {/* ─── INSTRUCTIONS MODAL ─── */}
{showInstructions && (
  <div className="modalOverlay" onClick={() => setShowInstructions(false)}>
    <div className="panel" onClick={e => e.stopPropagation()}>
      <button
        className="closeButton"
        onClick={() => setShowInstructions(false)}
      >
        &times;
      </button>
      <h3>How to Use the ODE Solver</h3>
      {/* Put your instructions text here */}
      <p>1. Hello! Welcome to Math 202 and Good luck!</p>
      <p>2. This solver is designed to provide you with a step by step solution for most differential equations in this course!</p>
      <p>3. A few tips: </p>
      <p>4. Make sure to use * to indciate multiplication: write xy as x*y.</p>
      <p>5. To input trig functions: write sinx as sin(x).</p>
      <p>6. For division, you can write x/y but its better to write x + 2/y as (x+2) / y.</p>
      <p>7. For square roots, write sqrt(x).</p>
      <p>8. You can upload and see uploaded documents, but maintain academic integraty. You can also subscribe to our email service. </p>
      {/* …etc… */}
    </div>
  </div>
)}  
      {/* ─── Order Selection ─── */}
      <div className="formGroup">
        <label>Select Order of the Differential Equation:</label>
        <select
          className="selectInput"
          value={order}
          onChange={e => {
            setOrder(e.target.value);
            setMethod("");
            setSecondCategory("");
            setOutput("");
            setEquation("");
            setSepFx(""); setSepGy(""); setSepFunc("");
            setAVal(""); setBVal(""); setCVal("");
            setMxy(""); setNxy(""); setY1Val(""); setY2Val(""); setFVal("");
          }}
        >
          <option value="">-- Select Order --</option>
          <option value="1">First Order</option>
          <option value="2">Second Order</option>
        </select>
      </div>
  
      {/* ─── FIRST ORDER SECTION ─── */}
{order === "1" && (
  <>
    <div className="formGroup">
      <label>Select a method:</label>
      <select
        className="selectInput"
        value={method}
        onChange={e => {
          setMethod(e.target.value);
          setOutput("");
          setEquation(""); setSepFx(""); setSepGy(""); setSepFunc("");
          setAVal(""); setBVal(""); setCVal("");
          setMxy(""); setNxy(""); setNVal("");
        }}
      >
        <option value="">-- Select Method --</option>
        {firstOrderMethods["1"].map(m => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>
    </div>

    {method && (
      <div className="noteBox">
        📌 <strong>Note:</strong> {methodInstructions[method]}
      </div>
    )}

    {method === "Separable" && (
      <div style={{ display: "flex", justifyContent: "center", gap: 20 }}>
        <input
          type="text"
          className="selectInput"
          placeholder="f(x)"
          value={sepFx}
          onChange={e => setSepFx(e.target.value)}
          style={{ width: 180 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="g(y)"
          value={sepGy}
          onChange={e => setSepGy(e.target.value)}
          style={{ width: 180 }}
        />
      </div>
    )}

    {method === "Linear" && (
      <div style={{ display: "flex", justifyContent: "center", gap: 20 }}>
        <input
          type="text"
          className="selectInput"
          placeholder="a(x)"
          value={aVal}
          onChange={e => setAVal(e.target.value)}
          style={{ width: 140 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="b(x)"
          value={bVal}
          onChange={e => setBVal(e.target.value)}
          style={{ width: 140 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="c(x)"
          value={cVal}
          onChange={e => setCVal(e.target.value)}
          style={{ width: 140 }}
        />
      </div>
    )}

    {method === "Exact / Integrating Factor / Homogeneous" && (
      <div style={{ display: "flex", justifyContent: "center", gap: 20 }}>
        <input
          type="text"
          className="selectInput"
          placeholder="M(x,y)"
          value={Mxy}
          onChange={e => setMxy(e.target.value)}
          style={{ width: 200 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="N(x,y)"
          value={Nxy}
          onChange={e => setNxy(e.target.value)}
          style={{ width: 200 }}
        />
      </div>
    )}

    {method === "Bernoulli" && (
      <div style={{ display: "flex", justifyContent: "center", gap: 20 }}>
        <input
          type="text"
          className="selectInput"
          placeholder="a(x)"
          value={aVal}
          onChange={e => setAVal(e.target.value)}
          style={{ width: 120 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="b(x)"
          value={bVal}
          onChange={e => setBVal(e.target.value)}
          style={{ width: 120 }}
        />
        <input
          type="text"
          className="selectInput"
          placeholder="c(x)"
          value={cVal}
          onChange={e => setCVal(e.target.value)}
          style={{ width: 120 }}
        />
        <input
          type="number"
          step="any"
          className="selectInput"
          placeholder="n"
          value={nVal}
          onChange={e => setNVal(e.target.value)}
          style={{ width: 120 }}
        />
      </div>
    )}

    {method === "Reduction to Separation of Variables" && (
      <div style={{ display: "flex", justifyContent: "center", gap: 20 }}>
        <input
          type="text"
          className="selectInput"
          placeholder="f(x)"
          value={sepFunc}
          onChange={e => setSepFunc(e.target.value)}
          style={{ width: 140 }}
        />
        <input
          type="number"
          step="any"
          className="selectInput"
          placeholder="A"
          value={aVal}
          onChange={e => setAVal(e.target.value)}
          style={{ width: 80 }}
        />
        <input
          type="number"
          step="any"
          className="selectInput"
          placeholder="B"
          value={bVal}
          onChange={e => setBVal(e.target.value)}
          style={{ width: 80 }}
        />
        <input
          type="number"
          step="any"
          className="selectInput"
          placeholder="C"
          value={cVal}
          onChange={e => setCVal(e.target.value)}
          style={{ width: 80 }}
        />
      </div>
    )}
  </>
)}
        {/* ─── SECOND‑ORDER SECTION ─── */}
      {order === "2" && (
        <>
          <div className="formGroup">
            <label>Select Second Order Category:</label>
            <select
              className="selectInput"
              value={secondCategory}
              onChange={e => {
                setSecondCategory(e.target.value);
                setMethod("");
                setOutput("");
                setAVal(""); setBVal(""); setCVal("");
                setY1Val(""); setY2Val(""); setFVal("");
              }}
            >
              <option value="">-- Select Category --</option>
              <option value="Homogeneous">Homogeneous</option>
              <option value="Non-Homogeneous">Non-Homogeneous</option>
            </select>
          </div>
          {secondCategory && (
            <div className="formGroup">
              <label>Select a method:</label>
              <select
                className="selectInput"
                value={method}
                onChange={e => {
                  setMethod(e.target.value);
                  setOutput("");
                  setAVal(""); setBVal(""); setCVal("");
                  setY1Val(""); setY2Val(""); setFVal("");
                }}
              >
                <option value="">-- Select Method --</option>
                {secondOrderMethods[secondCategory].map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          )}
          {method && (
            <div className="noteBox">
              📌 <strong>Note:</strong> {methodInstructions[method]}
            </div>
          )}
        {secondCategory && method && (
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "1rem",
                flexWrap: "wrap",
                marginBottom: "1.5rem",
              }}
            >
              {/* a, b, c placeholders vary by method */}
              {(method === "Homogeneous - Reduction of Order" ||
                method === "Non-Homogeneous - Variation of Parameters") ? (
                <>
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="a(x)"
                    value={aVal}
                    onChange={e => setAVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="b(x)"
                    value={bVal}
                    onChange={e => setBVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="c(x)"
                    value={cVal}
                    onChange={e => setCVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                </>
              ) : (
                <>
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="a"
                    value={aVal}
                    onChange={e => setAVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="b"
                    value={bVal}
                    onChange={e => setBVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="c"
                    value={cVal}
                    onChange={e => setCVal(e.target.value)}
                    style={{ width: "120px" }}
                  />
                </>
              )}

              {method === "Homogeneous - Reduction of Order" && (
                <input
                  type="text"
                  className="selectInput"
                  placeholder="y₁(x)"
                  value={y1Val}
                  onChange={e => setY1Val(e.target.value)}
                  style={{ width: "200px" }}
                />
              )}

              {(method === "Non-Homogeneous - Constant Coefficients" ||
                method === "Non-Homogeneous - Cauchy-Euler") && (
                <input
                  type="text"
                  className="selectInput"
                  placeholder="f(x)"
                  value={fVal}
                  onChange={e => setFVal(e.target.value)}
                  style={{ width: "200px" }}
                />
              )}

              {method === "Non-Homogeneous - Variation of Parameters" && (
                <>
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="y₁(x)"
                    value={y1Val}
                    onChange={e => setY1Val(e.target.value)}
                    style={{ width: "200px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="y₂(x)"
                    value={y2Val}
                    onChange={e => setY2Val(e.target.value)}
                    style={{ width: "200px" }}
                  />
                  <input
                    type="text"
                    className="selectInput"
                    placeholder="f(x)"
                    value={fVal}
                    onChange={e => setFVal(e.target.value)}
                    style={{ width: "200px" }}
                  />
                </>
              )}
        </div>
      )}          
   </>
  )}
  
      {/*
  Show Solve only when ready:
   – 1st order: order==="1" AND method is non‑empty
   – 2nd order: order==="2" AND secondCategory AND method are non‑empty
*/}
{((order === "1" && method) ||
  (order === "2" && secondCategory && method)) && (
  <div className="formGroup" style={{ textAlign: "center", marginTop: "1rem" }}>
    <button className="solveButton" onClick={handleSolve}>
      Solve
    </button>
  </div>
)}


  
      {/* ─── Output Section ─── */}
      <div className="outputBox">
        {output
          ? output.split("\n").map((line, idx) => {
              let txt = line.trim();
              if (!txt.startsWith("$")) txt = `$${txt}`;
              return (
                <div key={idx} style={{ marginBottom: "0.7rem" }}>
                  <Latex>{txt}</Latex>
                </div>
              );
            })
          : "Solution steps will appear here..."}
      </div>
  
      {/* ─── Bottom Buttons ─── */}
{output && (
  <div className="bottomButtonsWrapper">
    <div className="bottomButtons">
      {/* 1) Method‑specific reset */}
      <button className="newMethodButton" onClick={newMethodODE}>
        New {method} ODE
      </button>

      {/* 2) Reset at the order‑level */}
      {order === "1" ? (
        <button className="newFirstOrderButton" onClick={newFirstOrderODE}>
          New First Order ODE
        </button>
      ) : (
        <button className="newButton" onClick={newSecondOrderODE}>
          New Second Order ODE
        </button>
      )}

      {/* 3) Reset everything */}
      <button className="newButton" onClick={newODE}>
        New ODE
      </button>
    </div>
  </div>
)}

  
      
        {/* Instructions floating button */}
<button
  className="historyButton instructionsButton"
  onClick={() => setShowInstructions(true)}
>
  Instructions
</button>
  
      {/* ─── Bottom‑Left Email Actions ─── */}
<div className="bottomLeftActions">
  {/* Subscribe */}
  <div
    className="actionItem"
    onMouseEnter={() => setShowSubscribePanel(true)}
    onMouseLeave={() => setShowSubscribePanel(false)}
  >
    <button className="btn-subscribe">Subscribe</button>
    {showSubscribePanel && (
      <div className="bottomLeftPanel subscribePanel">
        <button className="closeSmall" onClick={() => setShowSubscribePanel(false)}>
          ×
        </button>
        <h4>Subscribe</h4>
        <input
          type="email"
          placeholder="Your email"
          value={subscriberEmail}
          onChange={e => setSubscriberEmail(e.target.value)}
        />
        <div style={{ marginTop: 8 }}>
          <button onClick={handleSubscribe}>OK</button>
        </div>
        {subscribeStatus && <p style={{ marginTop: 8 }}>{subscribeStatus}</p>}
      </div>
    )}
  </div>

  {/* Unsubscribe trigger */}
  <div className="actionItem">
    <button
      className="btn-unsubscribe"
      onClick={() => setShowUnsubscribeModal(true)}
    >
      Unsubscribe
    </button>
  </div>
  
  {/* ─── NEW: UNSUBSCRIBE MODAL ─── */}
  {showUnsubscribeModal && (
      <div
        className="modalOverlay"
        onClick={() => setShowUnsubscribeModal(false)}
      >
        <div className="panel" onClick={e => e.stopPropagation()}>
          <button
            className="closeButton"
            onClick={() => setShowUnsubscribeModal(false)}
          >
            &times;
          </button>
          <h3>Unsubscribe</h3>
          <p>Enter your email to unsubscribe:</p>
          <input
            type="email"
            placeholder="you@example.com"
            value={subscriberEmail}
            onChange={e => setSubscriberEmail(e.target.value)}
            style={{ width: "100%", margin: "0.5rem 0" }}
          />
          <button
            className="btn-unsubscribe"
            style={{ width: "100%" }}
            onClick={async () => {
              await handleUnsubscribe();
              // optionally auto‐close if successful:
              // if (subscribeStatus.startsWith("✅")) setShowUnsubscribeModal(false);
            }}
          >
            Confirm Unsubscribe
          </button>
          {subscribeStatus && (
            <p
              style={{
                marginTop: "0.75rem",
                color: subscribeStatus.startsWith("✅") ? "green" : "red"
              }}
            >
              {subscribeStatus}
            </p>
          )}
        </div>
      </div>
    )}


  {/* Fetch Email List */}
  <div
    className="actionItem"
    onMouseEnter={async () => {
      await handleFetchEmails();
      setShowFetchPanel(true);
    }}
    onMouseLeave={() => setShowFetchPanel(false)}
  >
    <button className="btn-fetch">Fetch Email List</button>
    {showFetchPanel && (
      <div className="bottomLeftPanel fetchPanel">
        <button className="closeSmall" onClick={() => setShowFetchPanel(false)}>
          ×
        </button>
        <h4>Subscribers</h4>
        {emailListStatus && <p>{emailListStatus}</p>}
        {emailList.length > 0 ? (
          <ul style={{ maxHeight: 150, overflowY: "auto" }}>
            {emailList.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        ) : (
          <p>No subscribers yet.</p>
        )}
      </div>
    )}
  </div>
</div>

    </div>
  );

}  

export default App;
