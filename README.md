# Asset Health API

A small Python service that tracks industrial assets, their **lifecycle status**
(ACTIVE, ACTIVE MATURE, END OF LIFE, DISCONTINUED) and their **obsolescence risk**,
packaged with Docker and deployed to **Kubernetes** locally and on **Azure (AKS)**.

Built to practice: Python · Docker · Kubernetes · Azure · CI with GitHub Actions · SRE basics (health probes, replicas, resource limits).

## Architecture

```
Developer ──push──▶ GitHub ──Actions──▶ tests + Docker build
                                   │
          Azure Container Registry (ACR) ◀── image
                                   │
          Azure Kubernetes Service (AKS)
             └─ Deployment (2 replicas, liveness/readiness probes)
             └─ Service (LoadBalancer) ──▶ public IP
             └─ ConfigMap (APP_ENV, APP_VERSION)
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info (environment, version) |
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe |
| GET | `/assets?lifecycle=END OF LIFE` | List assets (optional filter) with risk level |
| GET | `/assets/summary` | Totals by lifecycle and risk, out-of-stock items |
| GET | `/assets/{id}` | Single asset |
| GET | `/docs` | Interactive API docs (Swagger) |

**Risk rule:** HIGH = END OF LIFE/DISCONTINUED and no stock · MEDIUM = one of the two · LOW = otherwise.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -v
uvicorn app.main:app --reload    # http://localhost:8000/docs
```

## Run with Docker

```bash
docker build -t asset-health-api:1.0.0 .
docker run -p 8000:8000 asset-health-api:1.0.0
```

## Deploy to Kubernetes (minikube)

```bash
minikube start
minikube image load asset-health-api:1.0.0
kubectl apply -f k8s/
kubectl get pods
kubectl port-forward service/asset-health-api 8080:80   # http://localhost:8080/docs
```

## Deploy to Azure (AKS)

See [`GUIA_ES.md`](GUIA_ES.md) (Phase 4) for step-by-step Azure CLI commands.
**Remember to delete the resource group when finished to avoid charges.**

