import { defineConfig } from "vite";
import react from "@vitejs/plugin-react"; // Enables React-specific optimizations and HMR
import path from "path"; // Provides utilities for working with file and directory paths
import compression from "vite-plugin-compression";
import { viteExternalsPlugin } from "vite-plugin-externals";
// import { VitePWA } from "vite-plugin-pwa";

// const PWA = () => {
//   return VitePWA({
//     manifest: {
//       name: "Your App",
//       short_name: "App",
//       icons: [
//         {
//           src: "/icon-192.png",
//           sizes: "192x192",
//           type: "image/png",
//         },
//         {
//           src: "/icon-512.png",
//           sizes: "512x512",
//           type: "image/png",
//         },
//       ],
//     },
//   })
// }

// Export the Vite configuration
export default defineConfig({
  // base: "/app/",


  // Plugins section
  plugins: [
    viteExternalsPlugin({
      "react": "React",
      "react-dom": "ReactDOM",
      "bootstrap": "bootstrap",
      "@popperjs/core": "Popper",
    }),    
    react(), // Adds React plugin for handling JSX/TSX and fast refresh
    compression(), // Add gzip compression
  ],

  // Module resolution settings
  resolve: {
    preserveSymlinks: true, // Prevents breaking symbolic links, useful for monorepos
    alias: {
      // Define aliases for modules, resolving them to specific paths
    },
  },

  // Dependency optimization settings
  optimizeDeps: {
    include: [
      // List dependencies to pre-bundle for faster development
      'invariant',
      'classnames',
      'react-bootstrap',
    ],
    exclude: [
      // Exclude specific libraries or modules from optimization
    ],
  },

  // Development server configuration
  server: {
    proxy: {
      // Define proxy rules for API requests
      // Example: Requests to /api/gql are proxied to http://localhost:33001
      '/api': "http://localhost:7000"
    },
    watch: {
      // Specify paths to watch for changes
      ignored: [
        // Ensure certain packages are not ignored during file watching

      ],
    },
    hmr: {
      overlay: true, // Display overlay in the browser for HMR errors
    },
  },

  // Build options
build: {
  minify: false,  // ← Tímto Vite vypne minifikaci JS
  rollupOptions: {
    external: [
      "react",
      "react-dom",
      "react-router",
      "bootstrap",
      "@popperjs/core"
    ],
    output: {
      globals: {
        react: "React",
        "react-dom": "ReactDOM",
        
        bootstrap: "bootstrap",
        "@popperjs/core": "Popper"
      }
    }
  }
}

});
