import React from "react";

export function Modal({ title, children, onClose }) {
  return (
    <div style={styles.backdrop} onMouseDown={onClose}>
      <div style={styles.card} onMouseDown={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>{title}</h2>
          <button style={styles.close} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}

const styles = {
  backdrop: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.35)",
    display: "grid",
    placeItems: "center",
    padding: 16,
  },
  card: {
    width: "min(520px, 100%)",
    background: "white",
    borderRadius: 16,
    border: "1px solid #e5e7eb",
    padding: 16,
    boxShadow: "0 12px 40px rgba(0,0,0,0.18)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 12,
  },
  title: { margin: 0, fontSize: 18 },
  close: {
    border: "1px solid #e5e7eb",
    background: "white",
    borderRadius: 10,
    padding: "6px 10px",
    cursor: "pointer",
  },
};
