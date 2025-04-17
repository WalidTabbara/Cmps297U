import React, { useState, useRef } from "react";
import axios from "axios";
import Latex from "react-latex";
import "katex/dist/katex.min.css";
import "./App.css"; // Import the updated CSS file

// First order method options
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

// Second order: Two categories.
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
  Separable: "Input must be of the form dy/dx = f(x)*g(y).",
  Linear:
    "Input must be of the form a(x) dy/dx + b(x)y = c(x), where a(x) ≠ 0.",
  "Exact / Integrating Factor / Homogeneous":
    "Input must be of the form M(x, y) dx + N(x, y) dy = 0.",
  Bernoulli:
    "Input must be of the form a(x) dy/dx + b(x)y = c(x)yⁿ, where n ≠ 0 and n ≠ 1.",
  "Reduction to Separation of Variables":
    "Input must be of the form dy/dx = f(Ax+By+C). Provide f(x) and the constants A, B, C.",
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

function App() {
  // State declarations
  const [order, setOrder] = useState("");
  const [method, setMethod] = useState("");
  const [secondCategory, setSecondCategory] = useState("");
  const [equation, setEquation] = useState("");
  const [Mxy, setMxy] = useState("");
  const [Nxy, setNxy] = useState("");
  const [fInput, setFInput] = useState("");
  const [aVal, setAVal] = useState("");
  const [bVal, setBVal] = useState("");
  const [cVal, setCVal] = useState("");
  const [y1Val, setY1Val] = useState("");
  const [fVal, setFVal] = useState("");
  const [output, setOutput] = useState("");
  const [historyRecords, setHistoryRecords] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Reference for the equation textarea
  const equationRef = useRef(null);

  const independentVar = "x";
  const dependentVar = "y";

  // Helper: Insert text at caret position in the equation textarea
  const handleInsert = (insertText, cursorOffset) => {
    const textarea = equationRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue =
      equation.substring(0, start) + insertText + equation.substring(end);
    setEquation(newValue);
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + cursorOffset;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  // Load history from backend
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

  // Build payload and call backend solve endpoint
  const handleSolve = async () => {
    let payload = { x: independentVar, y: dependentVar };

    if (order === "1") {
      payload.order = order;
      payload.method = method;
      if (method === "Exact / Integrating Factor / Homogeneous") {
        payload.Mxy = Mxy;
        payload.Nxy = Nxy;
      } else {
        payload.equation = equation;
      }
    } else if (order === "2") {
      payload.order = order;
      payload.method = method;
      payload.a = aVal;
      payload.b = bVal;
      payload.c = cVal;
      if (method === "Homogeneous - Reduction of Order") {
        payload.y1 = y1Val;
      }
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

  // Reset functions for new ODEs
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
    <div className="container">
      <h1 className="header">ODE Solver</h1>

      {/* Order Selection */}
      <div className="formGroup">
        <label>Select Order of the Differential Equation:</label>
        <select
          className="selectInput"
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
        >
          <option value="">-- Select Order --</option>
          <option value="1">First Order</option>
          <option value="2">Second Order</option>
        </select>
      </div>

      {/* FIRST ORDER Section */}
      {order === "1" && (
        <>
          <div className="formGroup">
            <label>Select a method:</label>
            <select
              className="selectInput"
              value={method}
              onChange={(e) => {
                setMethod(e.target.value);
                setOutput("");
                setEquation("");
                setMxy("");
                setNxy("");
                setFInput("");
              }}
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
            <div className="noteBox">
              📌 <strong>Note:</strong> {methodInstructions[method]}
            </div>
          )}
          {method && (
            <div className="formGroup">
              <div className="tokenToolbar">
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("dy/dx", 0)}
                >
                  <Latex>{"$\\frac{dy}{dx}$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("sin()", 4)}
                >
                  <Latex>{"$\\sin(\\,)$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("cos()", 4)}
                >
                  <Latex>{"$\\cos(\\,)$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("tan()", 4)}
                >
                  <Latex>{"$\\tan(\\,)$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("^{ }", 2)}
                >
                  <Latex>{"$a^b$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert(" = ", 3)}
                >
                  <Latex>{"$=$"}</Latex>
                </button>
                <button
                  className="tokenButton"
                  onClick={() => handleInsert("log()", 4)}
                >
                  <Latex>{"$\\log(\\,)$"}</Latex>
                </button>
                <button
                  className="tokenButton"
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
                className="equationInput"
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
          <div className="formGroup">
            <label>Select Second Order Category:</label>
            <select
              className="selectInput"
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
                onChange={(e) => {
                  setMethod(e.target.value);
                  setOutput("");
                }}
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
            <div className="noteBox">
              📌 <strong>Note:</strong> {methodInstructions[method]}
            </div>
          )}
          {secondCategory && method && (
            <div className="formGroup">
              <label style={{ display: "block", marginBottom: "0.5rem" }}>
                Enter coefficients a, b, c:
              </label>
              <div>
                <input
                  type="text"
                  placeholder="a"
                  value={aVal}
                  onChange={(e) => setAVal(e.target.value)}
                  style={{ width: "18%", marginRight: "2%" }}
                />
                <input
                  type="text"
                  placeholder="b"
                  value={bVal}
                  onChange={(e) => setBVal(e.target.value)}
                  style={{ width: "18%", marginRight: "2%" }}
                />
                <input
                  type="text"
                  placeholder="c"
                  value={cVal}
                  onChange={(e) => setCVal(e.target.value)}
                  style={{ width: "18%" }}
                />
              </div>
              {method === "Homogeneous - Reduction of Order" && (
                <div style={{ marginTop: "1rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem" }}>
                    Enter a known solution y₁(x):
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. y₁(x)"
                    value={y1Val}
                    onChange={(e) => setY1Val(e.target.value)}
                    style={{ width: "60%" }}
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
                    type="text"
                    placeholder="e.g. f(x)"
                    value={fVal}
                    onChange={(e) => setFVal(e.target.value)}
                    style={{ width: "60%" }}
                  />
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Solve Button */}
      {((order === "1" && method) ||
        (order === "2" && secondCategory && method)) && (
        <div className="formGroup" style={{ textAlign: "center" }}>
          <button className="solveButton" onClick={handleSolve}>
            Solve
          </button>
        </div>
      )}

      {/* Output Section */}
      <div className="outputBox">
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

      {/* Bottom Buttons - wrapped in a centering container */}
      {((order === "1" && output) ||
  (order === "2" && output)) && (
  <div className="bottomButtonsWrapper">
    <div className="bottomButtons">
      {order === "1" ? (
        <>
          <button className="newSeparableButton" onClick={newSeparableODE}>
            New Separable ODE
          </button>
          <button className="newFirstOrderButton" onClick={newFirstOrderODE}>
            New First Order ODE
          </button>
        </>
      ) : (
        <button className="newButton" onClick={newSecondOrderODE}>
          New Second Order ODE
        </button>
      )}
      <button className="newButton" onClick={newODE}>
        New ODE
      </button>
    </div>
  </div>
)}

      {/* History Floating Button */}
      <button className="historyButton" onClick={toggleHistory}>
        History
      </button>

      {/* History Panel */}
      {isHistoryOpen && (
        <div className="historyPanel slideIn">
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
              <div key={idx} className="historyRecord">
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
