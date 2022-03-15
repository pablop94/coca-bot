# La Coca

La coca es un bot que nace para recordarnos a un grupo de amigues quienes tienen que hacer las compras para las juntadas.

## Comandos
`/agregar [nombre] [comida]` Con este comando agregamos una comida a la lista. Se enviará un recordatorio los días `REMINDER_DAYS` a las `REMINDER_HOUR_UTC` en punto, teniendo en cuenta el orden en el que fueron ingresadas.

`/historial` Con este comando vemos un contador histórico de quienes se encargaron de las comidas.

`/saltear` Con este comando Coca se saltea un recordatorio.

`/proximas` Con este comando Coca te muestra las próximas comidas.

`/borrar [id]` Con este comando Coca borra la comida con `id`.

`/resolver [id]` Con este comando Coca resuelve la comida con `id` antes del recordatorio.

## Variables de ambiente
- `CHAT_ID` el chat donde se enviará el recordatorio.
- `DEVELOPER_CHAT_ID` el chat donde se enviarán errores en caso de haberlos.
- `TELEGRAM_TOKEN` el token del bot de Telegram.
- `REMINDER_HOUR_UTC` la hora a la que se envía el recordatorio en UTC.
- `REMINDER_DAYS` los días en que se envía el recordatorio, 0 es lunes, 6 es domingo separado por coma. Por ejemplo 2,3 lo envía miercoles y jueves.
- `HISTORY_RESUME_DAY` el día del mes donde se envía el histórico de compras. Por defecto es 31 y si el mes no tiene 31, se envía el último día.
- `RANDOM_RUN_PROBABILITY` la probabilidad de que la coca envíe respuestas de audio. Por defecto es 50%.

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