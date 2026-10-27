# Taller/Auditor I2

El Taller I2 es un core local y neutral para una única acción sintética. Su proveedor/modelo efectivo son `synthetic-local`/`synthetic-action-v1`; fallback, red y subprocess son `none`/`deny-all`/`deny-all`.

Uso:

    python3 kit/scripts/bottega_taller.py preflight --casefile CASEFILE --grant GRANT.json --policy kit/taller/policy/taller-i2-v1.yaml
    python3 kit/scripts/bottega_taller.py create-initiative --casefile CASEFILE --grant GRANT.json --policy kit/taller/policy/taller-i2-v1.yaml --out .taller
    python3 kit/scripts/bottega_taller.py start-run --initiative INITIATIVE-SYNTHETIC-01 --idempotency-key idem-key-00000001 --operator operator-local-synthetic --store .taller
    python3 kit/scripts/bottega_auditor.py check --initiative INITIATIVE-SYNTHETIC-01 --snapshot .taller/INITIATIVE-SYNTHETIC-01/case.json --reviewer reviewer-local-synthetic

Los comandos mutantes exigen grant explícito, scope exacto, clasificación sintética y key idempotente. Los manifiestos son encadenados e inmutables; el replay de una key confirmada no ejecuta la acción otra vez. `PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL` y `PUBLICATION_AUTHORIZED` son decisiones independientes; el último permanece bloqueado en I2.

Límites I2: 3 stages, 5 artifacts por stage, 12 por iniciativa, 2 delivery attempts, 2 validation attempts, 300 segundos lógicos y 64 KiB por artifact. El resultado sintético no representa desempeño de producto ni costo de proveedor.

Reproducibilidad y regresión

La secuencia limpia canónica es `make setup` (usa exclusivamente `app01/package-lock.json`) seguida de `make ci`. No se instalan paquetes globales ni se usan proveedores reales. El escenario 429/fallback se documenta y ejercita únicamente mediante un fake sintético: primer 429 abre el circuito; fallback sólo se acepta con política explícita, proveedor y capability declarados.

Matriz I2.3: CLOSED→pause/resume (detects: terminalidad, idempotencia, cero manifiestos duplicados; does_not_detect: efectos de producción); tampering/truncado/hueco/hash forjado (detects: bloqueo al cargar y cadena payload/previous/sequence/eventos; does_not_detect: recuperación de un archivo ya destruido); expediente incompleto (detects: clasificación, grant, stages/gates, contadores, ledger y paquete de revisión ausentes); secreto en clave anidada (detects: BLOCKED sin exponer valor); self-review (detects: independencia); 429 fake (detects: circuit breaker y fallback autorizado; does_not_detect: proveedor real).
