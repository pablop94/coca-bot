# La Coca

La coca es un bot que nace para recordarnos a un grupo de amigues quienes tienen que hacer las compras para las juntadas.

## Modelo de configuración
El modelo `CocaSettings` contiene los siguientes atributos:
- `reminder_hour_utc` la hora a la que se envía el recordatorio en UTC.
- `reminder_day` el día en que se envía el recordatorio, 0 es lunes, 6 es domingo.
- `history_resume_day` el día del mes donde se envía el histórico de compras. Por defecto es 31 y si el mes no tiene 31, se envía el último día.
- `random_run_probability` la probabilidad de que la coca envíe respuestas de audio. Por defecto es 50%.

## Comandos
`/agregar nombre comida[, nombre2 comida2...]` Con este comando agregamos una comida a la lista. Se enviará un recordatorio el día `reminder_day` a las `reminder_hour_utc` en punto, teniendo en cuenta el orden en el que fueron ingresadas.
Se pueden agregar varias comidas enviando: 
```
/agregar nombre1 comida1, nombre2 comida2,nombre3 comida con muchas palabras
```

`/historial` Con este comando vemos un contador histórico de quienes se encargaron de las comidas.

`/saltear` Con este comando Coca se saltea un recordatorio.

`/proximas` Con este comando Coca te muestra las próximas comidas.

`/ultimas` Con este comando Coca te muestra las últimas 5 comidas.

`/borrar [id]` Con este comando Coca borra la comida con `id`.

`/resolver [id]` Con este comando Coca resuelve la comida con `id` antes del recordatorio.

`/copiar [id]` Con este comando Coca copia la comida con `id` con nuevas asignaciones.

`/recordatorio [lunes|martes|miercoles...]` Con este comando Coca cambia el día del recordatorio.

## Variables de ambiente
- `CHAT_ID` el chat donde se enviará el recordatorio.
- `DEVELOPER_CHAT_ID` el chat donde se enviarán errores en caso de haberlos.
- `TELEGRAM_TOKEN` el token del bot de Telegram.

## Ejecución
Estando en la carpeta `src`:

### Bot
```
python manage.py run_coca
```

### Tests
```
python manage.py test
```