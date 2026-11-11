
"use client";

import { useRef, useState } from "react";

const API_URL = "https://ai-video-knowledge-assistant.onrender.com";

const videos = [
  {
    id: "hmFQqjMF_f0",
    title: "How Playing Sports Benefits Your Body and Your Brain",
    source: "TED-Ed",
    category: "SPORT & BRAIN",
  },
  {
    id: "BHY0FxzoKZE",
    title: "The Brain-Changing Benefits of Exercise",
    source: "Wendy Suzuki (TED)",
    category: "NEUROSCIENCE",
  },
  {
    id: "OM-AeVyW1kk",
    title: "How the Heart Changes with Exercise",
    source: "Institute of Human Anatomy",
    category: "CARDIOVASCULAR",
  },
  {
    id: "Att-yGdYfgI",
    title: "Reduce Your Risk of Injury",
    source: "Rehab 2 Perform",
    category: "INJURY PREVENTION",
  },
    {
    id: "W2-UL8P610k",
    title: "Recovery Strategies for Athletes",
    source: "Karen Rossman (Tahoe Forest Health System)",
    category: "RECOVERY",
  },
  {
    id: "nUsmc4FgfBE",
    title: "What is Strength?",
    source: "Experts in Sport (Loughborough University)",
    category: "STRENGTH & CONDITIONING",
  },
  {
    id: "h2aWYjSA1Jc",
    title: "Sleep Toolkit: Tools for Optimizing Sleep & Sleep-Wake Timing",
    source: "Huberman Lab",
    category: "SLEEP & RECOVERY",
  },
  {
    id: "mLn2X2JSrbg",
    title: "Food is Fuel: Nutrients for Endurance, Optimal Sports Nutrition, and Handling Plateaus",
    source: "Mayo Clinic",
    category: "NUTRITION & HYDRATION",
  },
  {
    id: "RcGyVTAoXEU",
    title: "How to Make Stress Your Friend",
    source: "Kelly McGonigal (TED)",
    category: "STRESS & MENTAL WELLNESS",
  },
];

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [selectedVideo, setSelectedVideo] = useState<(typeof videos)[number] | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [status, setStatus] = useState("");

  async function selectVideo(video: (typeof videos)[number]) {
    setSelectedVideo(video);
    setMessages([]);
    setStatus("Loading video...");

    try {
      const response = await fetch(`${API_URL}/videos/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          youtube_url: `https://www.youtube.com/watch?v=${video.id}`,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        setStatus(
          typeof data.detail === "string"
            ? data.detail
            : "The selected video could not be loaded."
        );
        return;
      }

      setStatus("Video ready");
    } catch {
      setStatus("Unable to connect. Please try again.");
    }
  }

  async function sendMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!question.trim() || !selectedVideo || loading) return;

    const userMessage = question.trim();
    setQuestion("");
    setMessages((previous) => [
      ...previous,
      { role: "user", content: userMessage },
    ]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/agent-chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: selectedVideo.id,
          conversation_id: "web-" + selectedVideo.id,
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("The assistant could not answer.");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.answer },
      ]);
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I couldn't connect to the assistant. Please try again in a moment.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function toggleRecording() {
  if (recording) {
    mediaRecorderRef.current?.stop();
    setRecording(false);
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);

    audioChunksRef.current = [];
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    recorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());

      const audioBlob = new Blob(audioChunksRef.current, {
        type: recorder.mimeType || "audio/webm",
      });

      const extension = audioBlob.type.includes("mp4") ? "mp4" : "webm";
      const formData = new FormData();
      formData.append("file", audioBlob, `recording.${extension}`);

      setTranscribing(true);
      setStatus("Transcribing your question...");

      try {
        const response = await fetch(`${API_URL}/transcribe`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Audio transcription failed.");
        }

        setQuestion(data.text);
        setStatus("Transcription ready. Review your question before sending.");
      } catch (error) {
        setStatus(
          error instanceof Error ? error.message : "Audio transcription failed."
        );
      } finally {
        setTranscribing(false);
      }
    };

    recorder.start();
    setRecording(true);
    setStatus("Recording... Click the microphone again to stop.");
  } catch (error) {
    setStatus(
      error instanceof Error
        ? error.message
        : "Microphone access is unavailable."
    );
  }
}

  
return (
  <main className="min-h-screen">
    <header className="bg-[#102d4f] text-white">
      <div className="mx-auto flex max-w-[1500px] items-center justify-between px-6 py-5 md:px-10">
        <div>
          <div className="text-xl font-bold tracking-[0.16em]">
            THE <span className="text-[#b83a43]">PERFORMANCE</span> LAB
          </div>
          <div className="mt-1 text-[10px] tracking-[0.2em] text-blue-100">
            AI-POWERED SPORTS & WELLNESS KNOWLEDGE
          </div>
        </div>
        <div className="hidden font-serif text-lg italic md:block">
          Learn. Ask. Discover.
          <span className="ml-2 inline-block h-[2px] w-10 bg-[#b83a43] align-middle" />
        </div>
      </div>
    </header>

    <section className="border-b border-[#dce2e6] bg-[#e8f0f3]">
      <div className="mx-auto max-w-[1500px] px-6 py-12 md:px-10 md:py-16">
        <p className="mb-3 text-xs font-semibold tracking-[0.2em] text-[#287ca5]">
          SPORT · WELLNESS · PERFORMANCE
        </p>
        <h1 className="editorial-title max-w-3xl text-5xl leading-[1.05] text-[#102d4f] md:text-7xl">
          Explore the science of performance and wellbeing.
        </h1>
        <p className="editorial-text mt-5 max-w-2xl text-lg text-[#526575] md:text-xl">
          Discover ideas, understand the evidence, and ask questions about
          sport, exercise, sleep, nutrition and stress.
        </p>
        <div className="mt-7 h-1 w-16 bg-[#b83a43]" />
      </div>
    </section>

    <div className="mx-auto grid max-w-[1500px] gap-8 px-6 py-10 md:px-10 lg:grid-cols-[1.55fr_1fr]">
      <section>
        <div className="mb-6 flex items-center gap-3">
          <div className="h-8 w-1 bg-[#b83a43]" />
          <div>
            <h2 className="editorial-title text-3xl text-[#102d4f]">
              The video library
            </h2>
            <p className="mt-1 text-sm text-[#687785]">
              Nine selected videos. One place to explore.
            </p>
          </div>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {videos.map((video) => (
            <button
              key={video.id}
              onClick={() => selectVideo(video)}
              className={`group overflow-hidden rounded-lg border bg-white text-left shadow-sm transition hover:-translate-y-1 hover:shadow-lg ${
                selectedVideo?.id === video.id
                  ? "border-[#b83a43] ring-2 ring-[#b83a43]/20"
                  : "border-[#dce2e6]"
              }`}
            >
              <div className="relative aspect-video overflow-hidden bg-[#102d4f]">
                <img
                  src={`https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`}
                  alt={video.title}
                  className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                />
                <div className="absolute inset-0 flex items-center justify-center bg-[#102d4f]/10">
                  <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/95 text-xl text-[#102d4f] shadow">
                    ▶
                  </span>
                </div>
              </div>

              <div className="p-4">
                <p className="mb-2 text-[10px] font-bold tracking-[0.15em] text-[#287ca5]">
                  {video.category}
                </p>
                <h3 className="editorial-title text-lg leading-snug text-[#102d4f]">
                  {video.title}
                </h3>
                <p className="mt-2 text-sm text-[#687785]">
                  {video.source}
                </p>
                <div className="mt-4 h-[2px] w-8 bg-[#b83a43] transition-all group-hover:w-14" />
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="flex min-h-[600px] flex-col rounded-xl border border-[#dce2e6] bg-white p-5 shadow-sm md:p-7">
        <div className="border-b border-[#dce2e6] pb-5">
          <p className="text-xs font-semibold tracking-[0.18em] text-[#287ca5]">
            YOUR KNOWLEDGE SPACE
          </p>
          <h2 className="editorial-title mt-2 text-3xl text-[#102d4f]">
            Chat with the assistant
          </h2>
          <p className="mt-2 text-sm text-[#687785]">
            {selectedVideo
              ? selectedVideo.title
              : "Select a video from the library to begin."}
          </p>
          {status && (
            <p className="mt-3 text-xs text-[#287ca5]">{status}</p>
          )}
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto py-6">
          {!selectedVideo && (
            <div className="rounded-lg bg-[#e8f0f3] p-5">
              <p className="editorial-text text-lg text-[#102d4f]">
                Welcome.
              </p>
              <p className="mt-2 text-sm leading-relaxed text-[#526575]">
                Choose one of the nine videos. Then ask questions and explore
                its content with the AI assistant.
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`max-w-[90%] rounded-lg p-4 text-sm leading-relaxed ${
                message.role === "user"
                  ? "ml-auto bg-[#102d4f] text-white"
                  : "bg-[#e8f0f3] text-[#192b3d]"
              }`}
            >
              {message.content}
            </div>
          ))}

          {loading && (
            <p className="text-sm italic text-[#687785]">
              The assistant is thinking...
            </p>
          )}
        </div>

        <form onSubmit={sendMessage} className="border-t border-[#dce2e6] pt-5">
          <label htmlFor="question" className="sr-only">
            Your question
          </label>

          <div className="flex items-center gap-2 rounded-full border border-[#b8c8d4] bg-white p-2 focus-within:border-[#287ca5]">
            <input
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              disabled={!selectedVideo || loading || transcribing}
              placeholder={
                selectedVideo
                  ? "Type your question..."
                  : "Select a video first..."
              }
              className="min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-[#192b3d] outline-none placeholder:text-[#8997a3] disabled:cursor-not-allowed"
            />

            <button
              type="button"
              onClick={toggleRecording}
              disabled={!selectedVideo || loading || transcribing}
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-40 ${
                recording
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-[#287ca5] hover:bg-[#102d4f]"
              }`}
              aria-label={recording ? "Stop recording" : "Start voice recording"}
              title={recording ? "Stop recording" : "Start voice recording"}
            >
              {recording ? "Stop" : "Mic"}
            </button>

            <button
              type="submit"
              disabled={!selectedVideo || !question.trim() || loading || transcribing || recording}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#102d4f] text-xl text-white transition hover:bg-[#287ca5] disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Send question"
            >
              →
            </button>
          </div>

          {transcribing && (
            <p className="mt-2 text-xs text-[#287ca5]">
              Transcribing your question...
            </p>
          )}
        </form>
      </section>
    </div>

    <footer className="bg-[#102d4f] px-6 py-7 text-center text-white">
      <p className="editorial-text text-lg italic">
        Science. Sport. Better Performance.
      </p>
      <div className="mx-auto mt-3 h-[2px] w-14 bg-[#b83a43]" />
    </footer>
  </main>
);
}