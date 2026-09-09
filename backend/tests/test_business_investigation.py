from app.business_investigation.contracts import BusinessClues
from app.business_investigation.planner import BusinessQueryPlanner


def test_business_planner_uses_only_supplied_company_clues() -> None:
    clues = BusinessClues(
        company_name="Acme Robotics",
        domains=["acmerobotics.example"],
        industry="robotics",
        locations=["Vienna"],
        founders=["Alex Chen"],
        products=["warehouse robots"],
    )
    queries = BusinessQueryPlanner().plan(clues)
    rendered = [item.query for item in queries]
    assert '"Acme Robotics"' in rendered[0]
    assert any("robotics" in query for query in rendered)
    assert any("Alex Chen" in query for query in rendered)
    assert all("Acme Robotics" in query or "acmerobotics.example" in query for query in rendered)
