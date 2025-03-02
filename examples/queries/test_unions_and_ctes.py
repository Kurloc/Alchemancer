test_query = {
    "name": "testing names and stufffz",
    "query": {
        "select": {
            "union_query": {
                "id": {},
                "name": {},
            }
        },
        "union_all": {
            "name": "union_query",
            "left": {
                "select": {
                    "Role": {
                        "id": {},
                        "name": {},
                        "parent_role_id": {},
                    }
                },
                "alias": "cte_base",
            },
            "right": {
                "select": {
                    "cte_base": {
                        "id": {},
                        "name": {},
                    }
                },
                "joins": {
                    "Role": {
                        "select": {"id": {"label": "parent_role_id"}},
                        "where": {"Role.id__EQ": "cte_base.parent_role_id"},
                    }
                },
            },
            "cte": {
                "recursive": True,
                "name": "cte_base",
            },
        },
    },
    "expected_sql": """
with recursive cte_base(id, name, parent_role_id) as 
(
    SELECT 
        role.id as id,
        role.name as name,
        role.parent_role_id as parent_role_id
    FROM   role
    UNION all
    SELECT 
        anon_1.id as id,
        anon_1.name as name,
        role.id as parent_role_id
    FROM   
    (
        SELECT role.id as id,
            role.name as name,
            role.parent_role_id as parent_role_id
        FROM   role
    ) as anon_1 
    join role
    ON role.id = :id_1
)
SELECT cte_base.id,
       cte_base.name
FROM   cte_base
    """,
}
