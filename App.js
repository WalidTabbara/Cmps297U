import React, { useState, useRef } from "react";
import axios from "axios";
import Latex from "react-latex";
// IMPORTANT: Import KaTeX CSS so that LaTeX renders properly.
import "katex/dist/katex.min.css";

// First order method options (unchanged)
const firstOrderMethods = {
  "1": [
    "Separable",
    "Linear",
    "Exact / Integrating Factor / Homogeneous",
    "Bernoulli",
    "Reduction to Separation of Variables",
  ],
  "2": ["To be implemented"],
};

// Second order: Two categories for second order.
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

const methodInstructions = {
  // First Order Instructions
  Separable: "Input must be of the form dy/dx = f(x)*g(y).",
  Linear: "Input must be of the form a(x) dy/dx + b(x)y = c(x), where a(x) ≠ 0.",
  "Exact / Integrating Factor / Homogeneous":
    "Input must be of the form M(x, y) dx + N(x, y) dy = 0.",
  Bernoulli:
    "Input must be of the form a(x) dy/dx + b(x)y = c(x)yⁿ, where n ≠ 0 and n ≠ 1.",
  "Reduction to Separation of Variables":
    "Input must be of the form dy/dx = f(Ax+By+C). Provide f(x) and the constants A, B, C.",

  // Second Order Instructions:
  "Homogeneous - Reduction of Order":
    "Enter a(x), b(x), c(x) and y₁(x). Note: a(x) cannot be zero.",
  "Homogeneous - Constant Coefficients":
    "Enter constants a, b, c for ay''+by'+cy = 0. Note: a cannot be zero.",
  "Homogeneous - Cauchy-Euler":
    "Enter constants a, b, c for ax²y''+bxy'+cy = 0. Note: a cannot be zero.",
  "Non-Homogeneous - Constant Coefficients":
    "Enter constants a, b, c and the right-hand side f(x) for ay''+by'+cy = f(x). Note: a cannot be zero.",
  "Non-Homogeneous - Cauchy-Euler":
    "Enter constants a, b, c and the right-hand side f(x) for ax²y''+bxy'+cy = f(x). Note: a cannot be zero.",
  "Non-Homogeneous - Variation of Parameters":
    "Enter a(x), b(x), c(x) and the right-hand side f(x) for the non-homogeneous ODE. Note: a(x) must be nonzero.",
};

const baseButtonStyle = {
  padding: "8px 20px",
  color: "white",
  border: "none",
  cursor: "pointer",
  transition: "all 0.1s ease-in-out",
};

const solveButtonStyle = {
  ...baseButtonStyle,
  backgroundColor: "#007bff",
};

const newSeparableButtonStyle = {
  ...baseButtonStyle,
  backgroundColor: "#28a745",
};

const newFirstOrderButtonStyle = {
  ...baseButtonStyle,
  backgroundColor: "#17a2b8",
};

const newODEButtonStyle = {
  ...baseButtonStyle,
  backgroundColor: "#dc3545",
};

function App() {
  // Common state variables.
  const [order, setOrder] = useState(""); // "1" for first order, "2" for second order.
  const [method, setMethod] = useState("");
  const [secondCategory, setSecondCategory] = useState(""); // For order "2": "Homogeneous" or "Non-Homogeneous"
  const [equation, setEquation] = useState(""); // For first order equations.

  // First order extra fields.
  const [Mxy, setMxy] = useState("");
  const [Nxy, setNxy] = useState("");
  const [fInput, setFInput] = useState("");

  // Second order fields.
  const [aVal, setAVal] = useState("");
  const [bVal, setBVal] = useState("");
  const [cVal, setCVal] = useState("");
  // For Reduction of Order:
  const [y1Val, setY1Val] = useState("");
  // For Non-Homogeneous methods:
  const [fVal, setFVal] = useState("");

  const [output, setOutput] = useState("");

  // For history.
  const [historyRecords, setHistoryRecords] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Reference to the equation textarea.
  const equationRef = useRef(null);

  // Fixed variables.
  const independentVar = "x";
  const dependentVar = "y";

  // Helper: Insert text at current caret in the equation textarea.
  const handleInsert = (insertText, cursorOffset) => {
    const textarea = equationRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue = equation.substring(0, start) + insertText + equation.substring(end);
    setEquation(newValue);
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + cursorOffset;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  // Load history from backend.
  const loadHistory = async () => {
    try {
      const response = await axios.get("http://localhost:5000/history");
      setHistoryRecords(response.data.history || []);
    } catch (error) {
      console.error("Error loading history:", error);
    }
  };

  const toggleHistory = () => {
    if (!isHistoryOpen) {
      loadHistory();
    }
    setIsHistoryOpen(!isHistoryOpen);
  };

  // Build payload based on order and method then send to backend.
  const handleSolve = async () => {
    let payload = {
      x: independentVar,
      y: dependentVar,
    };

    if (order === "1") {
      // First order:
      payload.order = order;
      payload.method = method;
      if (method === "Exact / Integrating Factor / Homogeneous") {
        payload.Mxy = Mxy;
        payload.Nxy = Nxy;
      } else {
        payload.equation = equation;
      }
    } else if (order === "2") {
      // Second order:
      payload.order = order;
      payload.method = method;
      // Always send a, b, c.
      payload.a = aVal;
      payload.b = bVal;
      payload.c = cVal;
      if (method === "Homogeneous - Reduction of Order") {
        payload.y1 = y1Val;
      }
      // For non-homogeneous methods (including Variation of Parameters), send f.
      if (
        method === "Non-Homogeneous - Constant Coefficients" ||
        method === "Non-Homogeneous - Cauchy-Euler" ||
        method === "Non-Homogeneous - Variation of Parameters"
      ) {
        payload.f = fVal;
      }
    }

    try {
      const response = await axios.post("http://localhost:5000/solve", payload);
      setOutput(response.data.steps || "");
    } catch (error) {
      setOutput("Error solving the equation. Check the input and try again.");
    }
  };

  // Reset functions.
  const newSeparableODE = () => {
    setEquation("");
    setMxy("");
    setNxy("");
    setFInput("");
    setOutput("");
  };

  const newFirstOrderODE = () => {
    setMethod("");
    setEquation("");
    setMxy("");
    setNxy("");
    setFInput("");
    setOutput("");
  };

  const newSecondOrderODE = () => {
    setSecondCategory("");
    setMethod("");
    setAVal("");
    setBVal("");
    setCVal("");
    setY1Val("");
    setFVal("");
    setOutput("");
  };

  const newODE = () => {
    setOrder("");
    setSecondCategory("");
    setMethod("");
    setEquation("");
    setMxy("");
    setNxy("");
    setFInput("");
    setAVal("");
    setBVal("");
    setCVal("");
    setY1Val("");
    setFVal("");
    setOutput("");
  };

  return (
    <div
      style={{
        padding: "2rem",
        maxWidth: "900px",
        margin: "0 auto",
        position: "relative",
      }}
    >
      <h1 style={{ textAlign: "center" }}>ODE Solver</h1>

      {/* Order Selection */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Select Order of the Differential Equation:</label>
        <select
          value={order}
          onChange={(e) => {
            setOrder(e.target.value);
            setMethod("");
            setSecondCategory("");
            setOutput("");
            setEquation("");
            setMxy("");
            setNxy("");
            setFInput("");
            setAVal("");
            setBVal("");
            setCVal("");
            setY1Val("");
            setFVal("");
          }}
          style={{ padding: "8px", width: "100%", marginTop: "4px" }}
        >
          <option value="">-- Select Order --</option>
          <option value="1">First Order</option>
          <option value="2">Second Order</option>
        </select>
      </div>

      {/* FIRST ORDER Section */}
      {order === "1" && (
        <>
          <div style={{ marginBottom: "1rem" }}>
            <label>Select a method:</label>
            <select
              value={method}
              onChange={(e) => {
                setMethod(e.target.value);
                setOutput("");
                setEquation("");
                setMxy("");
                setNxy("");
                setFInput("");
              }}
              style={{ padding: "8px", width: "100%", marginTop: "4px" }}
            >
              <option value="">-- Select Method --</option>
              {firstOrderMethods["1"].map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          {method && methodInstructions[method] && (
            <div
              style={{
                marginBottom: "1rem",
                backgroundColor: "#fffbe6",
                padding: "10px 16px",
                border: "1px solid #ffe58f",
                borderRadius: "5px",
                fontStyle: "italic",
              }}
            >
              📌 <strong>Note:</strong> {methodInstructions[method]}
            </div>
          )}
          {method && (
            <div style={{ marginBottom: "1.5rem", textAlign: "center" }}>
              {/* Toolbar for common tokens */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "10px",
                  marginBottom: "10px",
                  flexWrap: "wrap",
                }}
              >
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("dy/dx", 0)}
                >
                  <Latex>{"$\\frac{dy}{dx}$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("sin()", 4)}
                >
                  <Latex>{"$\\sin(\\,)$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("cos()", 4)}
                >
                  <Latex>{"$\\cos(\\,)$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("tan()", 4)}
                >
                  <Latex>{"$\\tan(\\,)$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("^{ }", 2)}
                >
                  <Latex>{"$a^b$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert(" = ", 3)}
                >
                  <Latex>{"$=$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("log()", 4)}
                >
                  <Latex>{"$\\log(\\,)$"}</Latex>
                </button>
                <button
                  style={{ ...baseButtonStyle, backgroundColor: "#6c757d" }}
                  onClick={() => handleInsert("exp()", 4)}
                >
                  <Latex>{"$\\exp(\\,)$"}</Latex>
                </button>
              </div>
              <label style={{ display: "block", marginBottom: "0.5rem" }}>
                Enter your equation:
              </label>
              <textarea
                ref={equationRef}
                style={{
                  width: "80%",
                  padding: "12px",
                  fontSize: "1.1rem",
                  minHeight: "80px",
                  textAlign: "center",
                  resize: "vertical",
                }}
                placeholder="e.g. dy/dx = f(x)*g(y)"
                value={equation}
                onChange={(e) => setEquation(e.target.value)}
              />
            </div>
          )}
        </>
      )}

      {/* SECOND ORDER Section */}
      {order === "2" && (
        <>
          {/* Second Order Category Selection */}
          <div style={{ marginBottom: "1rem" }}>
            <label>Select Second Order Category:</label>
            <select
              value={secondCategory}
              onChange={(e) => {
                setSecondCategory(e.target.value);
                setMethod("");
                setOutput("");
                setAVal("");
                setBVal("");
                setCVal("");
                setY1Val("");
                setFVal("");
              }}
              style={{ padding: "8px", width: "100%", marginTop: "4px" }}
            >
              <option value="">-- Select Category --</option>
              <option value="Homogeneous">Homogeneous</option>
              <option value="Non-Homogeneous">Non-Homogeneous</option>
            </select>
          </div>
          {secondCategory && (
            <div style={{ marginBottom: "1rem" }}>
              <label>Select a method:</label>
              <select
                value={method}
                onChange={(e) => {
                  setMethod(e.target.value);
                  setOutput("");
                }}
                style={{ padding: "8px", width: "100%", marginTop: "4px" }}
              >
                <option value="">-- Select Method --</option>
                {secondOrderMethods[secondCategory].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          )}
          {method && methodInstructions[method] && (
            <div
              style={{
                marginBottom: "1rem",
                backgroundColor: "#fffbe6",
                padding: "10px 16px",
                border: "1px solid #ffe58f",
                borderRadius: "5px",
                fontStyle: "italic",
              }}
            >
              📌 <strong>Note:</strong> {methodInstructions[method]}
            </div>
          )}
          {/* Second Order Input Fields */}
          {secondCategory && method && (
            <div style={{ marginBottom: "1.5rem", textAlign: "center" }}>
              <label style={{ display: "block", marginBottom: "0.5rem" }}>
                Enter coefficients a, b, c:
              </label>
              <input
                style={{
                  width: "18%",
                  padding: "10px",
                  fontSize: "1.1rem",
                  marginRight: "2%",
                  textAlign: "center",
                }}
                placeholder="a"
                value={aVal}
                onChange={(e) => setAVal(e.target.value)}
              />
              <input
                style={{
                  width: "18%",
                  padding: "10px",
                  fontSize: "1.1rem",
                  marginRight: "2%",
                  textAlign: "center",
                }}
                placeholder="b"
                value={bVal}
                onChange={(e) => setBVal(e.target.value)}
              />
              <input
                style={{
                  width: "18%",
                  padding: "10px",
                  fontSize: "1.1rem",
                  textAlign: "center",
                }}
                placeholder="c"
                value={cVal}
                onChange={(e) => setCVal(e.target.value)}
              />
              <br />
              {method === "Homogeneous - Reduction of Order" && (
                <div style={{ marginTop: "1rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem" }}>
                    Enter a known solution y₁(x):
                  </label>
                  <input
                    style={{
                      width: "60%",
                      padding: "10px",
                      fontSize: "1.1rem",
                      textAlign: "center",
                    }}
                    placeholder="e.g. y₁(x)"
                    value={y1Val}
                    onChange={(e) => setY1Val(e.target.value)}
                  />
                </div>
              )}
              {(method === "Non-Homogeneous - Constant Coefficients" ||
                method === "Non-Homogeneous - Cauchy-Euler" ||
                method === "Non-Homogeneous - Variation of Parameters") && (
                <div style={{ marginTop: "1rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem" }}>
                    Enter the right-hand side f(x):
                  </label>
                  <input
                    style={{
                      width: "60%",
                      padding: "10px",
                      fontSize: "1.1rem",
                      textAlign: "center",
                    }}
                    placeholder="e.g. f(x)"
                    value={fVal}
                    onChange={(e) => setFVal(e.target.value)}
                  />
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Solve Button */}
      {((order === "1" && method) || (order === "2" && secondCategory && method)) && (
        <div style={{ textAlign: "center", marginBottom: "1rem" }}>
          <button
            style={solveButtonStyle}
            onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.95)")}
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onClick={handleSolve}
          >
            Solve
          </button>
        </div>
      )}

      {/* Output Section */}
      <div
        style={{
          marginTop: "1rem",
          background: "#f0f0f0",
          padding: "1rem",
          borderRadius: "6px",
          textAlign: "left",
          minHeight: "100px",
        }}
      >
        {output
          ? output.split("\n").map((line, idx) => {
              let trimmedLine = line.trim().replace(/\n/g, " ");
              if (!(trimmedLine.startsWith("$") && trimmedLine.endsWith("$"))) {
                trimmedLine = `$${trimmedLine}$`;
              }
              return (
                <div key={idx} style={{ marginBottom: "0.7rem" }}>
                  <Latex>{trimmedLine}</Latex>
                </div>
              );
            })
          : "Solution steps will appear here..."}
      </div>

      {/* New ODE Options Buttons */}
      {(order === "1" && output) || (order === "2" && output) ? (
        <div
          style={{
            marginTop: "1rem",
            display: "flex",
            flexDirection: "row",
            gap: "0.5rem",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {order === "1" ? (
            <>
              <button
                style={newSeparableButtonStyle}
                onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.95)")}
                onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
                onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
                onClick={newSeparableODE}
              >
                New Separable ODE
              </button>
              <button
                style={newFirstOrderButtonStyle}
                onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.95)")}
                onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
                onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
                onClick={newFirstOrderODE}
              >
                New First Order ODE
              </button>
            </>
          ) : (
            <button
              style={newODEButtonStyle}
              onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.95)")}
              onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
              onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
              onClick={newSecondOrderODE}
            >
              New Second Order ODE
            </button>
          )}
          <button
            style={newODEButtonStyle}
            onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.95)")}
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onClick={newODE}
          >
            New ODE
          </button>
        </div>
      ) : null}

      {/* History Floating Button (top right) */}
      <button
        style={{
          position: "fixed",
          top: "10px",
          right: "10px",
          padding: "10px 15px",
          backgroundColor: "#343a40",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          zIndex: 1000,
        }}
        onClick={toggleHistory}
      >
        History
      </button>

      {/* History Panel */}
      {isHistoryOpen && (
        <div
          style={{
            position: "fixed",
            top: "0",
            right: "0",
            width: "300px",
            height: "100%",
            backgroundColor: "#fff",
            boxShadow: "-2px 0 5px rgba(0,0,0,0.3)",
            zIndex: 1000,
            overflowY: "auto",
            padding: "20px",
          }}
        >
          <button
            style={{
              position: "absolute",
              top: "10px",
              right: "10px",
              background: "transparent",
              border: "none",
              fontSize: "18px",
              cursor: "pointer",
            }}
            onClick={toggleHistory}
          >
            &times;
          </button>
          <h2>History</h2>
          <p style={{ fontSize: "12px", color: "#777" }}>
            History refreshes every 4 months.
          </p>
          {historyRecords.length > 0 ? (
            historyRecords.map((record, idx) => (
              <div
                key={idx}
                style={{
                  borderBottom: "1px solid #ddd",
                  marginBottom: "10px",
                  paddingBottom: "10px",
                }}
              >
                <p>
                  <strong>Input:</strong> {record.input || "No input provided."}
                </p>
                <p>
                  <strong>Solution:</strong> {record.solution || "No solution provided."}
                </p>
              </div>
            ))
          ) : (
            <p>No history available.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

