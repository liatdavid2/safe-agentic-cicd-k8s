@echo off
setlocal

set NAMESPACE=%1
if "%NAMESPACE%"=="" set NAMESPACE=agentic-devops

set DEPLOYMENT=%2
if "%DEPLOYMENT%"=="" set DEPLOYMENT=orders-api

set OUTPUT_FILE=%3
if "%OUTPUT_FILE%"=="" set OUTPUT_FILE=artifacts\deployment_evidence.txt

if not exist artifacts mkdir artifacts

echo Collecting Kubernetes evidence...
echo Namespace: %NAMESPACE%
echo Deployment: %DEPLOYMENT%
echo Output file: %OUTPUT_FILE%

(
echo # Kubernetes Evidence
echo namespace=%NAMESPACE%
echo deployment=%DEPLOYMENT%
echo.

echo ## kubectl get deployment
kubectl get deployment %DEPLOYMENT% -n %NAMESPACE% -o wide
echo.

echo ## kubectl describe deployment
kubectl describe deployment %DEPLOYMENT% -n %NAMESPACE%
echo.

echo ## kubectl get pods
kubectl get pods -n %NAMESPACE% -o wide
echo.

echo ## kubectl get services
kubectl get services -n %NAMESPACE% -o wide
echo.

echo ## kubectl get events
kubectl get events -n %NAMESPACE% --sort-by=.lastTimestamp
echo.

echo ## kubectl logs deployment
kubectl logs deployment/%DEPLOYMENT% -n %NAMESPACE% --tail=120
echo.

echo ## rollout history
kubectl rollout history deployment/%DEPLOYMENT% -n %NAMESPACE%
echo.
) > "%OUTPUT_FILE%" 2>&1

echo Evidence saved to: %OUTPUT_FILE%