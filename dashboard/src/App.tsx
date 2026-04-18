import React, { useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Activity,
  HeartPulse,
  BedDouble,
  Waves,
  ShieldAlert,
  Clock3,
  Brain,
} from "lucide-react";

type HistoryItem = {
  time: string;
  event: string;
  status: string;
};

type DashboardData = {
  bedId: string;
  patientName: string;
  timestamp: string;
  vitals: {
    heartRate: number;
    respRate: number;
    spo2: number;
    movement: string;
  };
  normalized: {
    movementLevel: number;
    pressureRiskScore: number;
    edgeRisk: boolean;
    prolongedStaticPressure: boolean;
  };
  diagnosis: {
    alertLevel: string;
    eventType: string;
    rationale: string;
    action: string;
    confidence: number;
    emitAlert: boolean;
    suppressed: boolean;
  };
  history: HistoryItem[];
  heatmap: number[][];
  analysisSource?: string;
};

const Card = ({
  children,
  style = {},
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => (
  <div
    style={{
      background: "white",
      padding: "16px",
      borderRadius: "20px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
      border: "1px solid #e5e7eb",
      ...style,
    }}
  >
    {children}
  </div>
);

const CardHeader = ({ children }: { children: React.ReactNode }) => (
  <div style={{ marginBottom: "10px" }}>{children}</div>
);

const CardContent = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;

const CardTitle = ({ children }: { children: React.ReactNode }) => (
  <h3 style={{ margin: 0, fontSize: "20px", fontWeight: 700 }}>{children}</h3>
);

const Badge = ({
  children,
  style = {},
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => (
  <span
    style={{
      padding: "6px 10px",
      borderRadius: "999px",
      background: "#e5e7eb",
      fontSize: "12px",
      fontWeight: 600,
      ...style,
    }}
  >
    {children}
  </span>
);

const Button = ({
  children,
  onClick,
  active = false,
}: {
  children: React.ReactNode;
  onClick: () => void;
  active?: boolean;
}) => (
  <button
    onClick={onClick}
    style={{
      padding: "8px 12px",
      margin: "4px",
      borderRadius: "12px",
      border: active ? "1px solid #111827" : "1px solid #d1d5db",
      background: active ? "#111827" : "white",
      color: active ? "white" : "#111827",
      cursor: "pointer",
      fontWeight: 600,
    }}
  >
    {children}
  </button>
);

function normalizeMovementLabel(movement: string): string {
  const value = movement.toLowerCase();

  if (value === "low" || value === "bajo") return "Bajo";
  if (value === "moderate" || value === "moderado") return "Moderado";
  if (value === "high" || value === "alto") return "Alto";

  return movement;
}

function getMovementColor(movement: string): string {
  const value = movement.toLowerCase();

  if (value === "high" || value === "alto") return "#dc2626";
  if (value === "moderate" || value === "moderado") return "#d97706";
  return "#16a34a";
}

function getBadgeColor(status: string): React.CSSProperties {
  if (status === "high" || status === "critical") {
    return { background: "#fee2e2", color: "#b91c1c" };
  }
  if (status === "medium") {
    return { background: "#fef3c7", color: "#b45309" };
  }
  if (status === "suppressed") {
    return { background: "#e5e7eb", color: "#374151" };
  }
  if (status === "info") {
    return { background: "#dbeafe", color: "#1d4ed8" };
  }
  return { background: "#dcfce7", color: "#15803d" };
}

function getAlertPanelStyle(level: string): React.CSSProperties {
  if (level === "high" || level === "critical") {
    return {
      background: "#fef2f2",
      border: "1px solid #fecaca",
      color: "#991b1b",
    };
  }

  if (level === "medium") {
    return {
      background: "#fffbeb",
      border: "1px solid #fde68a",
      color: "#92400e",
    };
  }

  return {
    background: "#f0fdf4",
    border: "1px solid #bbf7d0",
    color: "#166534",
  };
}

function getHistoryItemStyle(status: string): React.CSSProperties {
  if (status === "high" || status === "critical") {
    return {
      background: "#fef2f2",
      border: "1px solid #fecaca",
    };
  }

  if (status === "medium") {
    return {
      background: "#fffbeb",
      border: "1px solid #fde68a",
    };
  }

  if (status === "suppressed") {
    return {
      background: "#f8fafc",
      border: "1px solid #cbd5e1",
    };
  }

  if (status === "info") {
    return {
      background: "#eff6ff",
      border: "1px solid #bfdbfe",
    };
  }

  return {
    background: "#f0fdf4",
    border: "1px solid #bbf7d0",
  };
}

function HeatCell({ value }: { value: number }) {
  const opacity = 0.15 + Math.max(0, Math.min(1, value)) * 0.85;
  return (
    <div
      style={{
        aspectRatio: "1 / 1",
        borderRadius: "18px",
        border: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "12px",
        fontWeight: 600,
        background: `rgba(239, 68, 68, ${opacity})`,
      }}
    >
      {value.toFixed(2)}
    </div>
  );
}

function RiskSemaphore({ level }: { level: string }) {
  const red = level === "high" || level === "critical";
  const yellow = level === "medium";
  const green = level === "low";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          padding: "12px",
          border: "1px solid #e5e7eb",
          borderRadius: "16px",
          background: "white",
        }}
      >
        <div
          style={{
            width: 24,
            height: 24,
            borderRadius: 999,
            background: red ? "#ef4444" : "#fecaca",
          }}
        />
        <div
          style={{
            width: 24,
            height: 24,
            borderRadius: 999,
            background: yellow ? "#facc15" : "#fde68a",
          }}
        />
        <div
          style={{
            width: 24,
            height: 24,
            borderRadius: 999,
            background: green ? "#22c55e" : "#bbf7d0",
          }}
        />
      </div>
      <div>
        <div style={{ fontSize: "14px", color: "#6b7280" }}>Semáforo de riesgo</div>
        <div style={{ fontSize: "20px", fontWeight: 700, textTransform: "capitalize" }}>
          {level}
        </div>
      </div>
    </div>
  );
}

function formatCentralDateTime(isoString: string): string {
  try {
    const date = new Date(isoString);

    return new Intl.DateTimeFormat("es-MX", {
      timeZone: "America/Mexico_City",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(date);
  } catch {
    return isoString;
  }
}

const SCENARIOS = [
  "normal_rest",
  "high_movement",
  "possible_false_alarm",
  "fall_risk",
  "pressure_ulcer_risk",
];

export default function App() {
  const [scenario, setScenario] = useState("fall_risk");
  const [source, setSource] = useState<"mongo" | "simulator">("mongo");
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [historyLog, setHistoryLog] = useState<HistoryItem[]>([]);
  const lastHistoryUpdateRef = useRef<number>(0);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const url =
        source === "mongo"
          ? "http://127.0.0.1:8000/status?source=mongo"
          : `http://127.0.0.1:8000/status?scenario=${scenario}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("No se pudo obtener el estado del paciente");
      }

      const result = await response.json();
      setData(result);

      if (result.history && result.history.length > 0) {
        const latestEvent = result.history[0];
        const now = Date.now();
        const isCriticalEvent =
          latestEvent.status === "high" || latestEvent.status === "critical";

        if (isCriticalEvent || now - lastHistoryUpdateRef.current >= 30000) {
          setHistoryLog((prev) => {
            const alreadyExists = prev.some(
              (item) =>
                item.time === latestEvent.time &&
                item.event === latestEvent.event &&
                item.status === latestEvent.status
            );
            
            if (alreadyExists) return prev;

            return [latestEvent, ...prev].slice(0, 8);
          });

          lastHistoryUpdateRef.current = now;
        }
      }
    } catch (err) {
      setError("Error al conectar con VITA-Sense AI");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 3000);

    return () => clearInterval(interval);
  }, [scenario, source]);

  if (loading && !data) {
    return <div style={{ padding: 24 }}>Cargando dashboard...</div>;
  }

  if (error && !data) {
    return <div style={{ padding: 24, color: "red" }}>{error}</div>;
  }

  if (!data) {
    return <div style={{ padding: 24 }}>Sin datos disponibles.</div>;
  }

  const { vitals, normalized, diagnosis, heatmap, analysisSource } = data;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        padding: 24,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1300, margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 16,
            flexWrap: "wrap",
            marginBottom: 24,
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                color: "#6b7280",
                fontSize: 14,
              }}
            >
              <BedDouble size={16} />
              <span>Web Dashboard · VITA-Sense</span>
            </div>

            <h1 style={{ margin: "8px 0 4px", fontSize: 32 }}>
              Monitoreo inteligente de cama hospitalaria
            </h1>

            <p style={{ margin: 0, color: "#6b7280" }}>
              Estado del paciente, heatmap, alerta visual e historial simple.
            </p>

            <div style={{ color: "#16a34a", fontWeight: "bold", marginTop: 8 }}>
              ● En monitoreo en tiempo real
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
            <div style={{ marginBottom: 8 }}>
              <Button onClick={() => setSource("mongo")} active={source === "mongo"}>
                Tiempo real (Mongo)
              </Button>
              <Button onClick={() => setSource("simulator")} active={source === "simulator"}>
                Simulador
              </Button>
            </div>

            {source === "simulator" && (
              <div>
                {SCENARIOS.map((key) => (
                  <Button key={key} onClick={() => setScenario(key)} active={scenario === key}>
                    {key.split("_").join(" ")}
                  </Button>
                ))}
              </div>
            )}
          </div>
        </div>

        {error && (
          <div style={{ marginBottom: 16, color: "#b91c1c", fontWeight: 600 }}>{error}</div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr",
            gap: 24,
            alignItems: "stretch",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <Card>
              <CardHeader>
                <CardTitle>Estado del paciente</CardTitle>
                <p style={{ margin: "8px 0 0", color: "#6b7280", fontSize: 14 }}>
                  {data.patientName} · {data.bedId} · actualización {formatCentralDateTime(data.timestamp)}
                </p>
              </CardHeader>
              <CardContent>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
                  <Card>
                    <CardContent>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <HeartPulse />
                        <div>
                          <div style={{ color: "#6b7280", fontSize: 14 }}>Frecuencia cardiaca</div>
                          <div style={{ fontSize: 28, fontWeight: 700 }}>
                            {vitals.heartRate}{" "}
                            <span style={{ fontSize: 14, color: "#6b7280" }}>bpm</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <Waves />
                        <div>
                          <div style={{ color: "#6b7280", fontSize: 14 }}>Respiración</div>
                          <div style={{ fontSize: 28, fontWeight: 700 }}>
                            {vitals.respRate}{" "}
                            <span style={{ fontSize: 14, color: "#6b7280" }}>rpm</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <Activity />
                        <div>
                          <div style={{ color: "#6b7280", fontSize: 14 }}>SpO2</div>
                          <div style={{ fontSize: 28, fontWeight: 700 }}>
                            {vitals.spo2}
                            <span style={{ fontSize: 14, color: "#6b7280" }}>%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <Clock3 />
                        <div>
                          <div style={{ color: "#6b7280", fontSize: 14 }}>Movimiento</div>
                          <div
                            style={{
                              fontSize: 28,
                              fontWeight: 700,
                              color: getMovementColor(vitals.movement),
                            }}
                          >
                            {normalizeMovementLabel(vitals.movement)}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              <Card>
                <CardHeader>
                  <CardTitle>Mapa de calor</CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    {heatmap.flat().map((value, idx) => (
                      <HeatCell key={idx} value={value} />
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Alerta visual</CardTitle>
                </CardHeader>
                <CardContent>
                  <div
                    style={{
                      padding: 16,
                      borderRadius: 18,
                      ...getAlertPanelStyle(diagnosis.alertLevel),
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <AlertTriangle size={18} />
                          <strong>{diagnosis.eventType}</strong>
                        </div>
                        <p style={{ marginTop: 10, lineHeight: 1.6 }}>{diagnosis.rationale}</p>
                        <div
                          style={{
                            marginTop: 10,
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                            fontSize: 13,
                            color: "#6b7280",
                          }}
                        >
                          <Brain size={14} />
                          <span>
                            Fuente de análisis:{" "}
                            {analysisSource === "gemini" ? "IA clínica" : "Reglas locales"}
                          </span>
                        </div>
                      </div>
                      <Badge style={getBadgeColor(diagnosis.alertLevel)}>
                        {diagnosis.alertLevel}
                      </Badge>
                    </div>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: 12,
                        marginTop: 16,
                      }}
                    >
                      <Card>
                        <CardContent>
                          <div style={{ fontSize: 12, textTransform: "uppercase", color: "#6b7280" }}>
                            Acción recomendada
                          </div>
                          <div style={{ marginTop: 6, fontWeight: 700 }}>{diagnosis.action}</div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent>
                          <div style={{ fontSize: 12, textTransform: "uppercase", color: "#6b7280" }}>
                            Confianza
                          </div>
                          <div style={{ marginTop: 6, fontWeight: 700 }}>
                            {Math.round(diagnosis.confidence * 100)}%
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>

                  <div
                    style={{
                      marginTop: 16,
                      border: "1px solid #e5e7eb",
                      borderRadius: 18,
                      padding: 16,
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 16,
                      flexWrap: "wrap",
                    }}
                  >
                    <RiskSemaphore level={diagnosis.alertLevel} />
                    <div style={{ color: "#4b5563", fontSize: 14 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                          marginBottom: 8,
                        }}
                      >
                        <ShieldAlert size={16} />
                        <span>Alerta emitida: {diagnosis.emitAlert ? "Sí" : "No"}</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <Clock3 size={16} />
                        <span>Suprimida por fatiga: {diagnosis.suppressed ? "Sí" : "No"}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <Card
              style={{
                minHeight: 460,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <CardHeader>
                <CardTitle>Historial simple</CardTitle>
              </CardHeader>
              <CardContent>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {historyLog.length === 0 ? (
                    <div
                      style={{
                        border: "1px solid #e5e7eb",
                        borderRadius: 16,
                        padding: 12,
                        color: "#6b7280",
                      }}
                    >
                      Aún no hay eventos registrados.
                    </div>
                  ) : (
                    historyLog.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          borderRadius: 16,
                          padding: 12,
                          ...getHistoryItemStyle(item.status),
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                          <strong>{item.event}</strong>
                          <Badge style={getBadgeColor(item.status)}>{item.time}</Badge>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div style={{ marginTop: 24 }}>
          <Card>
            <CardHeader>
              <CardTitle>Indicadores de riesgo</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: 16,
                }}
              >
                <Card>
                  <CardContent>
                    <div style={{ color: "#6b7280", fontSize: 14 }}>Movement level</div>
                    <div style={{ fontSize: 22, fontWeight: 700 }}>
                      {normalized.movementLevel.toFixed(2)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <div style={{ color: "#6b7280", fontSize: 14 }}>Edge risk</div>
                    <div style={{ fontSize: 22, fontWeight: 700 }}>
                      {normalized.edgeRisk ? "Activo" : "Inactivo"}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <div style={{ color: "#6b7280", fontSize: 14 }}>Pressure risk score</div>
                    <div style={{ fontSize: 22, fontWeight: 700 }}>
                      {normalized.pressureRiskScore.toFixed(3)}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}