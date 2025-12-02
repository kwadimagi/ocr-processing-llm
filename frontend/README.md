# Adamani AI RAG - Frontend

Modern Next.js frontend for invoice and PDF document processing with AI-powered RAG.

## Features

- 📄 **Document Upload** - Drag & drop PDF and image files
- 💬 **AI Chat Interface** - Ask questions about uploaded documents
- 🔍 **Source Attribution** - See which documents answer came from
- 💾 **Session Management** - Conversation history per user
- 🎨 **Beautiful UI** - Modern, responsive design with Tailwind CSS
- ⚡ **Real-time** - Instant feedback and processing status

## Prerequisites

- Node.js 18+ or Bun
- Backend API running on http://localhost:8080

## Installation

```bash
# Install dependencies
npm install
# or
bun install
```

## Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Development

```bash
# Start development server
npm run dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── globals.css   # Global styles
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Home page
│   ├── components/       # React components
│   │   ├── FileUploader.tsx
│   │   └── ChatInterface.tsx
│   ├── lib/              # Utilities
│   │   ├── api.ts        # API client
│   │   └── utils.ts      # Helper functions
│   └── types/            # TypeScript types
│       └── index.ts
├── public/               # Static assets
└── package.json
```

## Components

### FileUploader
- Drag & drop file upload
- File type validation
- OCR toggle for scanned PDFs
- Progress and error handling

### ChatInterface
- Real-time chat with AI
- Message history
- Source document display
- Session management

## API Integration

The frontend communicates with the backend API:

- `POST /documents/upload` - Upload files
- `POST /chat/` - Send chat messages
- `DELETE /chat/memory/{session_id}` - Clear history
- `GET /health` - Check backend status

## Usage

1. **Upload Documents**
   - Click or drag & drop PDF/image files
   - Toggle OCR for scanned documents
   - Wait for processing

2. **Ask Questions**
   - Type questions in the chat
   - Get AI-powered answers
   - View source documents

3. **Manage Sessions**
   - Each user gets a unique session
   - Clear history with the trash button

## Docker

Build and run with Docker:

```bash
# Build
docker build -t adamani-frontend .

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8080 \
  adamani-frontend
```

## Customization

### Styling
- Edit `tailwind.config.ts` for theme
- Modify `src/app/globals.css` for global styles

### API
- Update `NEXT_PUBLIC_API_URL` in `.env.local`
- Modify `src/lib/api.ts` for new endpoints

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 8080
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` is correct

### Build Errors
- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## Technologies

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## License

MIT
