# Technical Comparison: Documentation Generators

To determine the optimal tool for technical documentation requiring mathematical notation support and version control integration, the following generators were evaluated based on their architectural and CI/CD characteristics:

| Feature | MkDocs (Material) | Docusaurus | Hugo |
| :--- | :--- | :--- | :--- |
| **Renderelési modell** | Statikus (Python/Jinja2) | Reaktív (React/SPA) | Statikus (Go) |
| **Függőségi lánc** | Python (pip), izolált | Node.js (npm), komplex | Go (bináris) |
| **Képletmegjelenítés** | Native (KaTeX/MathJax) | Plugin-függő (Remark) | Native (Goldmark) |
| **Verziókezelés** | Git-native (file-based) | Komplex (i18n/versioning) | File-based |
| **Build pipeline** | Egyszerű, determinisztikus | Webpack/Vite alapú | Ultra-gyors Go bináris |

## Engineering Rationale (A választás indoklása)

The selection of **MkDocs with the Material theme** was based on the following technical requirements:

1.  **Build Pipeline Isolation:** The project's primary development environment is Node.js-based. Utilizing a Python-based documentation generator (pip) ensures complete decoupling of the documentation build process from the project's dependency tree. This prevents potential `node_modules` conflicts and ensures a deterministic build pipeline.



2.  **SSR vs. Hydration Overhead:** Docusaurus (React-based) uses a Single Page Application (SPA) architecture, introducing "hydration" (client-side runtime initialization) overhead. MkDocs generates pure, static HTML at build-time, which guarantees optimal page load performance and superior search engine indexing without runtime JavaScript dependencies.

3.  **Mathematical Integrity:** Benchmark metrics (statistical distribution, standard deviation, p99) require robust LaTeX rendering. MkDocs Material provides native KaTeX/MathJax integration that functions reliably without the runtime JavaScript versioning conflicts often observed in Remark-plugin-based React implementations.

4.  **Version Control Efficiency:** As a project utilizing trunk-based development, the ability to resolve merge conflicts is critical. MkDocs maintains documentation in strict Markdown files, minimizing metadata clutter and resulting in clean, manageable Git diffs compared to the templating-heavy or SPA-meta-data-rich alternatives.