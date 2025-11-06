export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Settings</h2>
      <div className="space-y-2">
        <p>
          This frontend reads the backend URL from <code>NEXT_PUBLIC_BACKEND_URL</code>.
          On Vercel, set it in Project Settings → Environment Variables.
        </p>
        <p>
          The backend supports optional Gemini integration via <code>GEMINI_API_KEY</code> to
          improve glossary definitions and question generation.
        </p>
      </div>
      <div className="text-sm text-gray-600">
        Tip: When running locally, expose your backend with ngrok and set
        <code> NEXT_PUBLIC_BACKEND_URL=https://YOUR_TUNNEL.ngrok.io</code>.
      </div>
    </div>
  );
}


