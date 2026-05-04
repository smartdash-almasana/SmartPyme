"""
AdmissionService — Capa 1: Admisión Epistemológica
TS_ADM_002_ADMISSION_SERVICE_MINIMO

Servicio mínimo determinístico que procesa el mensaje inicial del dueño
y produce un InitialCaseAdmission.

Reglas:
- Sin IA ni modelos de lenguaje.
- Sin OperationalCase.
- Sin diagnóstico.
- Sin fórmulas.
- Detección por keywords simples sobre el mensaje en minúsculas.
- Prioridad clínica: SANGRIA > INESTABILIDAD > OPTIMIZACION.

Documento rector: docs/product/SMARTPYME_CAPA_01_ADMISION_EPISTEMOLOGICA.md
"""

from __future__ import annotations

import uuid

from app.contracts.admission_contract import (
    EvidenceItem,
    EvidenceTask,
    InitialCaseAdmission,
    OwnerDemand,
    PathologyCandidate,
    Person,
    SymptomCandidate,
)

# ---------------------------------------------------------------------------
# Conjuntos de keywords por dominio
# ---------------------------------------------------------------------------

# Caso SANGRIA — pérdida económica activa o sospecha fuerte
_SANGRIA_KEYWORDS: frozenset[str] = frozenset(
    [
        "plata",
        "caja",
        "contador",
        "gastos",
        "sueldos",
        "negro",
        "blanco",
        "no me dan los números",
        "no me dan los numeros",
        "no sé dónde se me va",
        "no se donde se me va",
        "me están robando",
        "me estan robando",
        "no me cierra",
        "resultado",
        "ganancias",
        "pérdida",
        "perdida",
    ]
)

# Caso INESTABILIDAD — desorden operativo
_STOCK_KEYWORDS: frozenset[str] = frozenset(
    [
        "stock",
        "precios",
        "pantalones",
        "inventario",
        "excel",
        "paulita",
        "jean",
        "talle",
        "modelo",
        "revendedor",
        "mercadería",
        "mercaderia",
        "productos",
        "depósito",
        "deposito",
    ]
)


def _contains_any(text: str, keywords: frozenset[str]) -> bool:
    """Devuelve True si el texto (ya en minúsculas) contiene alguna keyword."""
    return any(kw in text for kw in keywords)


def _mentions_paulita(text: str) -> bool:
    return "paulita" in text


def _mentions_excel(text: str) -> bool:
    return "excel" in text


def _mentions_contador(text: str) -> bool:
    return "contador" in text


def _mentions_sueldos(text: str) -> bool:
    return "sueldos" in text or "sueldo" in text


def _mentions_gastos(text: str) -> bool:
    return "gastos" in text or "gasto" in text


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


class AdmissionService:
    """
    Servicio de admisión epistemológica mínimo y determinístico.

    Uso:
        service = AdmissionService()
        result = service.process(cliente_id="cliente_x", owner_message="...")
        # result es un InitialCaseAdmission
    """

    def process(self, cliente_id: str, owner_message: str) -> InitialCaseAdmission:
        """
        Procesa el mensaje inicial del dueño y produce un InitialCaseAdmission.

        Prioridad de detección: SANGRIA > INESTABILIDAD > OPTIMIZACION.
        No diagnostica. No crea OperationalCase. No llama modelos.
        """
        msg = owner_message.lower()
        case_id = str(uuid.uuid4())

        is_sangria = _contains_any(msg, _SANGRIA_KEYWORDS)
        is_stock = _contains_any(msg, _STOCK_KEYWORDS)

        if is_sangria:
            return self._build_sangria_case(case_id, cliente_id, owner_message, msg)
        elif is_stock:
            return self._build_stock_case(case_id, cliente_id, owner_message, msg)
        else:
            return self._build_generic_case(case_id, cliente_id, owner_message)

    # ------------------------------------------------------------------
    # Caso SANGRIA
    # ------------------------------------------------------------------

    def _build_sangria_case(
        self,
        case_id: str,
        cliente_id: str,
        owner_message: str,
        msg_lower: str,
    ) -> InitialCaseAdmission:
        people: list[Person] = []
        evidence: list[EvidenceItem] = []
        tasks: list[EvidenceTask] = []

        # Persona: contador
        if _mentions_contador(msg_lower):
            person_contador = Person(
                person_id="person_contador",
                name="contador",
                role="Asesor contable externo",
            )
            people.append(person_contador)

            ev_gastos = EvidenceItem(
                evidence_id="ev_reporte_contador_gastos",
                evidence_type="reporte_contador_gastos",
                format="pdf",
                responsible_person_id="person_contador",
                epistemic_state="DUDA",
                confidence=0.6,
                notes="Reporte de gastos blancos del mes.",
            )
            evidence.append(ev_gastos)

            tasks.append(
                EvidenceTask(
                    task_id="task_reporte_contador",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_reporte_contador_gastos",
                    responsible_person_id="person_contador",
                    instruction="Pedir al contador el reporte de gastos blancos del mes.",
                )
            )

        # Evidencia: sueldos
        if _mentions_sueldos(msg_lower):
            ev_sueldos = EvidenceItem(
                evidence_id="ev_excel_sueldos",
                evidence_type="excel_sueldos",
                format="xlsx",
                epistemic_state="DUDA",
                confidence=0.5,
                notes="Excel de sueldos blanco y negro.",
            )
            evidence.append(ev_sueldos)

            tasks.append(
                EvidenceTask(
                    task_id="task_excel_sueldos",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_excel_sueldos",
                    instruction="Subir el Excel de sueldos (blanco y negro).",
                )
            )

        # Si hay gastos mencionados pero no sueldos ni contador, crear evidencia genérica
        if _mentions_gastos(msg_lower) and not _mentions_contador(msg_lower) and not _mentions_sueldos(msg_lower):
            ev_gastos_gen = EvidenceItem(
                evidence_id="ev_gastos_generales",
                evidence_type="reporte_gastos_generales",
                format="xlsx",
                epistemic_state="DUDA",
                confidence=0.4,
                notes="Detalle de gastos del período.",
            )
            evidence.append(ev_gastos_gen)

            tasks.append(
                EvidenceTask(
                    task_id="task_gastos_generales",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_gastos_generales",
                    instruction="Reunir detalle de gastos del período (Excel, PDF o listado).",
                )
            )

        # Si no hay ninguna evidencia aún (solo menciona caja/plata sin más detalle)
        if not evidence:
            ev_caja = EvidenceItem(
                evidence_id="ev_caja_general",
                evidence_type="reporte_caja_general",
                format="xlsx",
                epistemic_state="DUDA",
                confidence=0.4,
                notes="Información de caja o movimientos de dinero.",
            )
            evidence.append(ev_caja)

            tasks.append(
                EvidenceTask(
                    task_id="task_caja_general",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_caja_general",
                    instruction=(
                        "Para entender el flujo de dinero necesito ventas, gastos y "
                        "movimientos de caja del período. ¿Podés compartirlos?"
                    ),
                )
            )

        demand = OwnerDemand(
            raw_text=owner_message,
            explicit_objective="Entender dónde se va el dinero y consolidar el resultado real.",
            inferred_objectives=[
                "Detectar sangría económica activa.",
                "Consolidar caja blanca y caja negra.",
                "Calcular resultado real del período.",
            ],
            area="caja",
            urgency=5,
        )

        return InitialCaseAdmission(
            case_id=case_id,
            cliente_id=cliente_id,
            demand=demand,
            clinical_phase="SANGRIA",
            people=people,
            sources=[],
            evidence=evidence,
            tasks=tasks,
            symptoms=[
                SymptomCandidate(symptom_id="caja_fragmentada", confidence=0.9),
                SymptomCandidate(symptom_id="resultado_real_desconocido", confidence=0.85),
            ],
            pathologies=[
                PathologyCandidate(
                    pathology_id="resultado_real_no_calculable",
                    score=0.85,
                    reason="El dueño no puede calcular su resultado real por falta de consolidación.",
                ),
                PathologyCandidate(
                    pathology_id="caja_partida_no_conciliada",
                    score=0.75,
                    reason="Existen múltiples flujos de dinero no integrados.",
                ),
            ],
            next_step=(
                "Para entender dónde se va el dinero necesito: "
                "ventas del período, gastos (blancos e informales) y movimientos de caja. "
                "¿Podés compartir esa información?"
            ),
        )

    # ------------------------------------------------------------------
    # Caso INESTABILIDAD — stock
    # ------------------------------------------------------------------

    def _build_stock_case(
        self,
        case_id: str,
        cliente_id: str,
        owner_message: str,
        msg_lower: str,
    ) -> InitialCaseAdmission:
        people: list[Person] = []
        evidence: list[EvidenceItem] = []
        tasks: list[EvidenceTask] = []

        # Persona: Paulita
        if _mentions_paulita(msg_lower):
            person_paulita = Person(
                person_id="person_paulita",
                name="Paulita",
                role="Administración interna",
            )
            people.append(person_paulita)

        # Evidencia: Excel de stock (si menciona Excel o Paulita)
        if _mentions_excel(msg_lower) or _mentions_paulita(msg_lower):
            responsible = "person_paulita" if _mentions_paulita(msg_lower) else None
            ev_excel = EvidenceItem(
                evidence_id="ev_excel_stock",
                evidence_type="Excel_stock",
                format="xlsx",
                responsible_person_id=responsible,
                epistemic_state="DUDA",
                confidence=0.6,
                notes="Excel de stock y precios mencionado por el dueño.",
            )
            evidence.append(ev_excel)

            tasks.append(
                EvidenceTask(
                    task_id="task_excel_stock",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_excel_stock",
                    responsible_person_id=responsible,
                    instruction=(
                        "Pedir el Excel de stock y precios"
                        + (" a Paulita." if _mentions_paulita(msg_lower) else ".")
                    ),
                )
            )

        # Si no hay Excel ni Paulita pero sí stock/inventario
        if not evidence:
            ev_inv = EvidenceItem(
                evidence_id="ev_inventario",
                evidence_type="inventario_fisico",
                format="xlsx",
                epistemic_state="DUDA",
                confidence=0.4,
                notes="Inventario o listado de stock disponible.",
            )
            evidence.append(ev_inv)

            tasks.append(
                EvidenceTask(
                    task_id="task_inventario",
                    task_type="REQUEST_EVIDENCE",
                    evidence_id="ev_inventario",
                    instruction=(
                        "Para ordenar el stock necesito un listado de productos con "
                        "cantidades y precios. ¿Tenés algo así disponible?"
                    ),
                )
            )

        demand = OwnerDemand(
            raw_text=owner_message,
            explicit_objective="Ordenar stock y precios para tener control operativo.",
            inferred_objectives=[
                "Conocer el stock real disponible.",
                "Actualizar precios de venta.",
                "Registrar ventas de forma directa.",
            ],
            area="stock",
            urgency=3,
        )

        return InitialCaseAdmission(
            case_id=case_id,
            cliente_id=cliente_id,
            demand=demand,
            clinical_phase="INESTABILIDAD",
            people=people,
            sources=[],
            evidence=evidence,
            tasks=tasks,
            symptoms=[
                SymptomCandidate(symptom_id="stock_desordenado", confidence=0.9),
                SymptomCandidate(symptom_id="precios_desactualizados", confidence=0.75),
            ],
            pathologies=[
                PathologyCandidate(
                    pathology_id="inventario_no_confiable",
                    score=0.85,
                    reason="Stock declarado sin conteo físico confirmado.",
                ),
                PathologyCandidate(
                    pathology_id="precios_no_gobernados",
                    score=0.7,
                    reason="Precios no actualizados o no disponibles.",
                ),
            ],
            next_step=(
                "Para ordenar el stock necesito el Excel de stock y precios"
                + (" de Paulita." if _mentions_paulita(msg_lower) else ".")
                + " ¿Podés conseguirlo?"
            ),
        )

    # ------------------------------------------------------------------
    # Caso genérico — OPTIMIZACION
    # ------------------------------------------------------------------

    def _build_generic_case(
        self,
        case_id: str,
        cliente_id: str,
        owner_message: str,
    ) -> InitialCaseAdmission:
        demand = OwnerDemand(
            raw_text=owner_message,
            explicit_objective="Mejorar el negocio (objetivo a precisar).",
            inferred_objectives=[],
            area="mixto",
            urgency=2,
        )

        return InitialCaseAdmission(
            case_id=case_id,
            cliente_id=cliente_id,
            demand=demand,
            clinical_phase="OPTIMIZACION",
            people=[],
            sources=[],
            evidence=[],
            tasks=[],
            symptoms=[],
            pathologies=[],
            next_step=(
                "Para poder ayudarte necesito entender mejor el problema. "
                "¿Qué área querés mejorar: ventas, costos, stock, caja u operaciones? "
                "Contame con más detalle qué está pasando."
            ),
        )
