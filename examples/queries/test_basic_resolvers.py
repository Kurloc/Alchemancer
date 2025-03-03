test_query = {
    "name": __name__,
    "query": {
        "select": {
            "RecursiveRolesResolver()": {
                "role_id": {},
                "role_name": {},
                "role_parent_id": {},
            }
        },
        "resolver_args": {"role_id": 1},
    },
    "expected_sql": """
WITH RECURSIVE roles_base_cte(role_id, role_name, role_parent_id) AS
                   (SELECT "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id        AS role_id,
                           "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_name      AS role_name,
                           "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id AS role_parent_id
                    FROM "TEMP__ALCHEMANCER_TYPES_RESOLVER"
                    UNION ALL
                    SELECT anon_1.role_id AS role_id, anon_1.role_name AS role_name, role.id AS role_parent_id
                    FROM (SELECT "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id        AS role_id,
                                 "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_name      AS role_name,
                                 "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id AS role_parent_id
                          FROM "TEMP__ALCHEMANCER_TYPES_RESOLVER") AS anon_1
                             JOIN role ON role.id = anon_1.role_parent_id
                    WHERE anon_1.role_id = :role_id_1
                       OR anon_1.role_parent_id = :role_parent_id_1)
SELECT roles_base_cte.role_id, roles_base_cte.role_name, roles_base_cte.role_parent_id
FROM roles_base_cte
    """,
}
