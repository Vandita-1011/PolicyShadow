"""Deletes all failed and stale/stuck-running runs from the database."""

import sys
from policyshadow.persistence.db import SessionLocal
from policyshadow.persistence.models import RunModel, ClusterModel, ViolationModel, RecommendationModel, DecisionModel
from policyshadow.persistence.run_store import RunStore

def cleanup_stale_runs():
    store = RunStore()
    with SessionLocal() as session:
        stale_runs = session.query(RunModel).filter(
            RunModel.status.in_(["failed", "running"])
        ).order_by(RunModel.created_at.desc()).all()
        
        if not stale_runs:
            print("No failed or stale running runs found in database.")
            return

        print(f"Found {len(stale_runs)} stale/failed run(s) to delete:\n")
        deleted_ids = []
        for r in stale_runs:
            print(f"  - run_id: {r.run_id}")
            print(f"    status:   {r.status}")
            print(f"    created:  {r.created_at}")
            err = (r.error[:100] + '...') if r.error else 'None'
            print(f"    error:    {err}\n")
            deleted_ids.append(r.run_id)

    # Delete each run using RunStore.delete_run (which cascades to clusters, violations, recommendations, decisions)
    for rid in deleted_ids:
        success = store.delete_run(rid)
        print(f"Deleted run {rid}: {'SUCCESS' if success else 'FAILED'}")

    # Verify remaining runs
    with SessionLocal() as session:
        remaining_stale = session.query(RunModel).filter(
            RunModel.status.in_(["failed", "running"])
        ).count()
        total_remaining = session.query(RunModel).count()
        print(f"\nVerification:")
        print(f"Remaining failed/running runs: {remaining_stale}")
        print(f"Total remaining active runs:   {total_remaining} (all completed)")

if __name__ == "__main__":
    cleanup_stale_runs()
