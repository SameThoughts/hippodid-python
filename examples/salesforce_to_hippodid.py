"""
End-to-end batch: CSV -> character template -> batch create -> verify.

Shows the full Salesforce-style pipeline:
1. Create a character template with field mappings
2. Batch create characters from a CSV data source
3. Poll job status until completion
4. Verify created characters

Requirements: pip install hippodid pandas
"""

import time

from hippodid import HippoDid

hd = HippoDid(api_key="hd_your_key")

# ── Step 1: Create a character template ──────────────────────────────────────

template = hd.create_character_template(
    name="Sales Rep Template",
    description="Template for onboarding sales reps from CRM export",
    categories=[
        {"categoryName": "preferences", "purpose": "Communication and work preferences"},
        {"categoryName": "deals", "purpose": "Active and historical deal information"},
        {"categoryName": "relationships", "purpose": "Key client relationships"},
    ],
    default_values={"role": "Sales Representative"},
    field_mappings=[
        {"sourceColumn": "rep_name", "targetCategory": "", "targetField": "name"},
        {"sourceColumn": "territory", "targetCategory": "", "targetField": "description"},
        {"sourceColumn": "crm_id", "targetCategory": "", "targetField": "externalId"},
    ],
)
print(f"Created template: {template.id}")

# ── Step 2: Batch create from data ──────────────────────────────────────────

rows = [
    {"rep_name": "Alice Johnson", "territory": "West Coast", "crm_id": "SF-001"},
    {"rep_name": "Bob Smith", "territory": "East Coast", "crm_id": "SF-002"},
    {"rep_name": "Carol Lee", "territory": "Midwest", "crm_id": "SF-003"},
]

job = hd.batch_create_characters(
    template_id=template.id,
    data=rows,
    external_id_column="crm_id",
    on_conflict="SKIP",
)
print(f"Started batch job: {job.job_id} (status: {job.status})")

# ── Step 3: Poll until completion ────────────────────────────────────────────

while job.status not in ("COMPLETED", "FAILED"):
    time.sleep(2)
    job = hd.get_batch_job_status(job.job_id)
    p = job.progress
    print(f"  Progress: {p.processed}/{p.total} (succeeded={p.succeeded}, failed={p.failed})")

print(f"Job finished: {job.status}")

# ── Step 4: Verify characters were created ───────────────────────────────────

for row in rows:
    char = hd.get_character_by_external_id(row["crm_id"])
    print(f"  {char.name} (id={char.id}, external_id={char.external_id})")
