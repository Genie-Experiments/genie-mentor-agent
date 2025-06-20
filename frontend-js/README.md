# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Professional Enhancements

This project uses industry-standard tools such as ESLint with type-checked configurations, Fast Refresh via [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react) or [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc), ensuring quality and efficiency in development.

## Node Setup

Ensure you have Node.js (version 14 or later) installed. Download it from [nodejs.org](https://nodejs.org) and verify the installation with `node -v`.

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed on your machine

### Running with Docker

1. **Build and run the frontend in isolation:**

   ```bash
   docker build -t genie-mentor-frontend .
   docker run -p 3001:80 genie-mentor-frontend
   ```

   This will make the frontend available at `http://localhost:3001`.

2. **Running as part of the entire project:**
   From the project root directory:
   ```bash
   docker-compose up -d
   ```
   This will start all services including the frontend.

### Development with Docker

For development with live reload capabilities:

```bash
docker-compose -f docker-compose.dev.yml up frontend
```

### Integration with Backend Services

The frontend is configured to communicate with:

- `agent-service` - Main agent service
- `data-ingestion-service` - Service for data ingestion
- Gateway services for external integrations

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x';
import reactDom from 'eslint-plugin-react-dom';

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
});
```

## Getting Started

1. Install dependencies: `npm install`
2. Run the development server: `npm run dev`
3. Build for production: `npm run build`

## Contributing

We welcome contributions. Please ensure:

- Code follows our style guidelines.
- All tests pass.
- Relevant documentation is updated.

## Troubleshooting Docker Setup

### Common Issues

1. **Port conflicts:**

   - If port 3001 is already in use, modify the port mapping in docker-compose.yml

2. **Container build failures:**

   - Check logs with `docker-compose logs frontend`
   - Rebuild with `docker-compose build --no-cache frontend`

3. **Connection to backend services:**
   - Ensure all dependent services are running
   - Check network configuration in docker-compose.yml
