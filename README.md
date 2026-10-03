# Gemelo Digital de Consumidores de Telefonía

Prototipo docente para la materia **Comercialización – Facultad de Ingeniería – UNLZ**.

## Objetivo

Mostrar de manera simple cómo una representación digital de consumidores puede utilizarse para:

- representar un mercado;
- segmentar consumidores;
- probar ofertas comerciales;
- simular cambios en precio, GB, cobertura y promociones;
- observar qué perfiles reaccionarían;
- discutir la diferencia entre modelo digital y gemelo digital.

## Importante

Los 100 consumidores incluidos son **sintéticos**. No representan datos reales de Claro, Personal, Movistar ni del mercado argentino.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Crear un repositorio en GitHub.
2. Subir `app.py`, `requirements.txt` y `README.md`.
3. Entrar a Streamlit Community Cloud.
4. Seleccionar el repositorio.
5. Indicar `app.py` como Main file path.
6. Hacer Deploy.

## Estructura didáctica

**Consumidores reales → datos → modelo digital → simulación → decisión → nueva medición → actualización**
