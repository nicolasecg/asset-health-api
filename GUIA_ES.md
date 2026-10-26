# Guía del proyecto: Asset Health API

**Objetivo:** construir una API en Python que muestre el estado de ciclo de vida y el riesgo de obsolescencia de activos industriales, empaquetarla en Docker, desplegarla en Kubernetes en tu PC y luego en Azure.

Está basada en lo que ya hago en Rockwell (ciclo de vida, stock, obsolescencia). Los datos de `app/assets.json` son ficticios: **no se van a subir datos reales de clientes ni de Rockwell a GitHub.**

---

## Fase 0 · Preparar herramientas 
Instala: **Python 3.12**, **VS Code**, **Git**, **Docker Desktop**, **minikube**, **kubectl** y **Azure CLI**.
Crea un repo público en GitHub llamado `asset-health-api` y sube estos archivos.

## Fase 1 · Python 
1. Crea el entorno virtual e instala dependencias (comandos en el README).
2. Corre `pytest -v`: deben pasar 5 pruebas.
3. Corre `uvicorn app.main:app --reload` y abre `http://localhost:8000/docs`. Prueba cada endpoint.
 

## Fase 2 · Docker 
1. `docker build -t asset-health-api:1.0.0 .`
2. `docker run -p 8000:8000 asset-health-api:1.0.0`
3. Lee el `Dockerfile` línea por línea y entiende cada una (ojo: la app corre sin usuario root).


## Fase 3 · Kubernetes local con minikube 
```bash
minikube start
minikube image load asset-health-api:1.0.0
kubectl apply -f k8s/
kubectl get pods            # debes ver 2 pods en Running
kubectl port-forward service/asset-health-api 8080:80
```
**Experimentos SRE (lo más valioso de la fase):**
- **Autorreparación:** `kubectl delete pod <nombre>` y mira cómo Kubernetes crea otro.
- **Escalar:** `kubectl scale deployment asset-health-api --replicas=4`
- **Ambientes:** cambia `APP_ENV` a `qa` en `k8s/configmap.yaml`, aplica de nuevo, `kubectl rollout restart deployment asset-health-api` y verifica en `/`.
- **Fallo controlado:** en `deployment.yaml` cambia la ruta del `readinessProbe` a `/noexiste`, aplica y observa con `kubectl describe pod` por qué el pod no queda listo. Luego corrígelo.

**Qué aprendes:** Deployment, Service, ConfigMap, probes, réplicas, límites de recursos.

## Fase 4 · Azure: AKS + ACR 
> ⚠️ **Esto cuesta dinero.** Usa la cuenta gratuita de Azure o los créditos que tengas, crea todo en **un solo grupo de recursos** y **bórralo el mismo día** que termines. Revisa en el portal *Cost Management*.

```bash
az login
# Nombres (el del ACR debe ser único en todo Azure, solo minúsculas y números)
RG=rg-asset-health
LOC=eastus
ACR=acrassethealth$RANDOM
AKS=aks-asset-health

az group create --name $RG --location $LOC
az acr create --resource-group $RG --name $ACR --sku Basic

# Construye la imagen en la nube (no necesitas subirla desde tu PC)
az acr build --registry $ACR --image asset-health-api:1.0.0 .

# Cluster pequeño de 1 nodo, conectado al ACR
az aks create --resource-group $RG --name $AKS \
  --node-count 1 --tier free \
  --attach-acr $ACR --generate-ssh-keys

az aks get-credentials --resource-group $RG --name $AKS
```
Antes de aplicar los manifiestos:
- En `k8s/deployment.yaml` cambia `image:` por `<TU_ACR>.azurecr.io/asset-health-api:1.0.0`.
- En `k8s/service.yaml` cambia `type: ClusterIP` por `type: LoadBalancer`.

```bash
kubectl apply -f k8s/
kubectl get service asset-health-api --watch   # espera la EXTERNAL-IP
```
Abre `http://<EXTERNAL-IP>/docs`. **Toma capturas de pantalla para el README.**

**Limpieza (obligatoria):**
```bash
az group delete --name $RG --yes --no-wait
```


## Fase 5 · CI con GitHub Actions 
El archivo `.github/workflows/ci.yml` ya corre las pruebas y construye la imagen en cada push. Revisa la pestaña **Actions** del repo.

---
