import React, { useState } from "react";
import { SafeAreaView, View, Text, TextInput, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from "react-native";

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || "http://10.0.2.2:8000";

export default function App() {
  const [pdfUrl, setPdfUrl] = useState("https://arxiv.org/pdf/1706.03762.pdf"); // Transformer paper
  const [question, setQuestion] = useState("What is this document about?");
  const [contexts, setContexts] = useState<string[]>([]);
  const [answer, setAnswer] = useState("");
  const [ingestLoading, setIngestLoading] = useState(false);
  const [queryLoading, setQueryLoading] = useState(false);
  const [quizLoading, setQuizLoading] = useState(false);
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);
  const [showQuiz, setShowQuiz] = useState(false);
  const [pdfIngested, setPdfIngested] = useState(false);

  const ingest = async () => {
    setErr(""); setSuccess(""); setPdfIngested(false);
    setIngestLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/rag/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_url: pdfUrl }),
      });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || "Failed to ingest PDF");
      }
      const data = await res.json();
      setSuccess(`✅ Successfully ingested PDF! Added ${data.added || 0} chunks.`);
      setPdfIngested(true);
      Alert.alert("Success", `PDF ingested successfully! Added ${data.added || 0} chunks to the knowledge base.`);
    } catch (e: any) {
      setErr(e.message || "Failed to ingest PDF");
      Alert.alert("Error", e.message || "Failed to ingest PDF");
    } finally {
      setIngestLoading(false);
    }
  };

  const ask = async () => {
    if (!question.trim()) {
      Alert.alert("Error", "Please enter a question");
      return;
    }
    setErr(""); setSuccess(""); setContexts([]); setAnswer("");
    setQueryLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), top_k: 5 }),
      });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || "Failed to query");
      }
      const data = await res.json();
      setAnswer(data.answer || "No answer generated.");
      setContexts(data.contexts || []);
    } catch (e: any) {
      setErr(e.message || "Failed to query");
      Alert.alert("Error", e.message || "Failed to query");
    } finally {
      setQueryLoading(false);
    }
  };

  const generateQuiz = async () => {
    if (!pdfIngested) {
      Alert.alert("Warning", "Please ingest a PDF first before generating quiz questions.");
      return;
    }
    setErr(""); setSuccess(""); setQuizQuestions([]); setShowQuiz(true);
    setQuizLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/rag/quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_questions: numQuestions }),
      });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || "Failed to generate quiz");
      }
      const data = await res.json();
      if (data.questions && data.questions.length > 0) {
        setQuizQuestions(data.questions);
        setSuccess(`✅ Generated ${data.questions.length} quiz questions!`);
      } else {
        setErr("No quiz questions generated. Make sure you've ingested a PDF first.");
      }
    } catch (e: any) {
      setErr(e.message || "Failed to generate quiz");
      Alert.alert("Error", e.message || "Failed to generate quiz");
    } finally {
      setQuizLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f5f7fa" }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Header */}
        <View style={{ backgroundColor: "#4a90e2", padding: 20, borderRadius: 12, marginBottom: 20 }}>
          <Text style={{ fontSize: 24, fontWeight: "bold", color: "#fff", marginBottom: 4 }}>
            🎓 AI Edu Assessment
          </Text>
          <Text style={{ fontSize: 12, color: "#e8f4f8" }}>RAG-Powered Learning Platform</Text>
        </View>

        {/* PDF Ingestion Section */}
        <View style={{ backgroundColor: "#fff", padding: 16, borderRadius: 12, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 }}>
          <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 12, color: "#2c3e50" }}>📄 PDF Ingestion</Text>
          <Text style={{ fontSize: 14, color: "#7f8c8d", marginBottom: 8 }}>Enter PDF URL (research paper, document, etc.)</Text>
          <TextInput
            value={pdfUrl}
            onChangeText={setPdfUrl}
            placeholder="https://arxiv.org/pdf/..."
            style={{
              borderWidth: 1,
              borderColor: "#ddd",
              padding: 12,
              borderRadius: 8,
              backgroundColor: "#fafafa",
              fontSize: 14,
              marginBottom: 12,
            }}
            multiline
          />
          <TouchableOpacity
            onPress={ingest}
            disabled={ingestLoading}
            style={{
              backgroundColor: ingestLoading ? "#95a5a6" : "#27ae60",
              padding: 14,
              borderRadius: 8,
              alignItems: "center",
            }}
          >
            {ingestLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={{ color: "#fff", fontWeight: "600", fontSize: 16 }}>Ingest PDF</Text>
            )}
          </TouchableOpacity>
          {pdfIngested && (
            <View style={{ marginTop: 8, padding: 8, backgroundColor: "#d4edda", borderRadius: 6 }}>
              <Text style={{ color: "#155724", fontSize: 12 }}>✓ PDF ready for queries and quiz generation</Text>
            </View>
          )}
        </View>

        {/* Q&A Section */}
        <View style={{ backgroundColor: "#fff", padding: 16, borderRadius: 12, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 }}>
          <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 12, color: "#2c3e50" }}>❓ Ask Questions</Text>
          <Text style={{ fontSize: 14, color: "#7f8c8d", marginBottom: 8 }}>Ask questions about the ingested document</Text>
          <TextInput
            value={question}
            onChangeText={setQuestion}
            placeholder="What is this document about?"
            style={{
              borderWidth: 1,
              borderColor: "#ddd",
              padding: 12,
              borderRadius: 8,
              backgroundColor: "#fafafa",
              fontSize: 14,
              marginBottom: 12,
              minHeight: 50,
            }}
            multiline
          />
          <TouchableOpacity
            onPress={ask}
            disabled={queryLoading}
            style={{
              backgroundColor: queryLoading ? "#95a5a6" : "#3498db",
              padding: 14,
              borderRadius: 8,
              alignItems: "center",
            }}
          >
            {queryLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={{ color: "#fff", fontWeight: "600", fontSize: 16 }}>Ask Question</Text>
            )}
          </TouchableOpacity>

          {answer ? (
            <View style={{ marginTop: 16, padding: 16, backgroundColor: "#e8f5e9", borderRadius: 8, borderLeftWidth: 4, borderLeftColor: "#4caf50" }}>
              <Text style={{ fontSize: 16, fontWeight: "600", marginBottom: 12, color: "#2c3e50" }}>💡 Answer:</Text>
              <Text 
                style={{ 
                  fontSize: 15, 
                  color: "#34495e", 
                  lineHeight: 24,
                  textAlign: "left",
                }}
                selectable={true}
              >
                {answer.split('\n').map((line, idx) => (
                  <Text key={idx}>
                    {line.trim()}{'\n'}
                  </Text>
                ))}
              </Text>
            </View>
          ) : null}
        </View>

        {/* Quiz Generation Section */}
        <View style={{ backgroundColor: "#fff", padding: 16, borderRadius: 12, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 }}>
          <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 12, color: "#2c3e50" }}>📝 Generate Quiz</Text>
          <Text style={{ fontSize: 14, color: "#7f8c8d", marginBottom: 8 }}>Number of Questions</Text>
          <TextInput
            value={String(numQuestions)}
            onChangeText={(t) => {
              const num = parseInt(t) || 5;
              setNumQuestions(Math.max(1, Math.min(20, num)));
            }}
            keyboardType="numeric"
            style={{
              borderWidth: 1,
              borderColor: "#ddd",
              padding: 12,
              borderRadius: 8,
              backgroundColor: "#fafafa",
              fontSize: 14,
              marginBottom: 12,
            }}
          />
          <TouchableOpacity
            onPress={generateQuiz}
            disabled={quizLoading || !pdfIngested}
            style={{
              backgroundColor: quizLoading || !pdfIngested ? "#95a5a6" : "#9b59b6",
              padding: 14,
              borderRadius: 8,
              alignItems: "center",
            }}
          >
            {quizLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={{ color: "#fff", fontWeight: "600", fontSize: 16 }}>
                {pdfIngested ? "Generate Quiz" : "Ingest PDF First"}
              </Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Quiz Questions Display */}
        {showQuiz && quizQuestions?.length > 0 ? (
          <View style={{ backgroundColor: "#fff", padding: 16, borderRadius: 12, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 }}>
            <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 16, color: "#2c3e50" }}>📚 Quiz Questions</Text>
            {quizQuestions.map((q, i) => (
              <View key={i} style={{ marginBottom: 20, padding: 16, backgroundColor: "#f8f9fa", borderRadius: 10, borderWidth: 1, borderColor: "#e9ecef" }}>
                <Text style={{ fontSize: 16, fontWeight: "600", marginBottom: 12, color: "#2c3e50" }}>
                  Q{i + 1}. {q.question}
                </Text>
                {q.choices?.map((choice: string, idx: number) => (
                  <View key={idx} style={{ marginLeft: 8, marginBottom: 8, padding: 8, backgroundColor: "#fff", borderRadius: 6 }}>
                    <Text style={{ fontSize: 14, color: "#34495e" }}>
                      {String.fromCharCode(65 + idx)}. {choice}
                    </Text>
                  </View>
                ))}
                <View style={{ marginTop: 12, padding: 10, backgroundColor: "#d4edda", borderRadius: 6 }}>
                  <Text style={{ fontSize: 14, fontWeight: "600", color: "#155724" }}>
                    ✓ Correct Answer: {q.correct}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        ) : showQuiz && !quizLoading ? (
          <View style={{ backgroundColor: "#fff3cd", padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <Text style={{ color: "#856404", fontSize: 14 }}>
              ⚠️ No quiz questions generated. Make sure you've ingested a PDF first.
            </Text>
          </View>
        ) : null}

        {/* Error/Success Messages */}
        {err ? (
          <View style={{ backgroundColor: "#f8d7da", padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <Text style={{ color: "#721c24", fontSize: 14 }}>❌ {err}</Text>
          </View>
        ) : null}

        {success ? (
          <View style={{ backgroundColor: "#d4edda", padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <Text style={{ color: "#155724", fontSize: 14 }}>{success}</Text>
          </View>
        ) : null}

        {/* Footer */}
        <View style={{ padding: 12, alignItems: "center" }}>
          <Text style={{ fontSize: 12, color: "#95a5a6" }}>Backend: {BACKEND_URL}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
