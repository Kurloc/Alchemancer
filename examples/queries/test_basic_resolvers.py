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
with recursive roles_base_cte(role_id, role_name, role_parent_id) as (SELECT "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id as role_id,
                                                                             "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_name as role_name,
                                                                             "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id as role_parent_id
                                                                      FROM   "TEMP__ALCHEMANCER_TYPES_RESOLVER"
                                                                      WHERE  "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id = :role_id_1
                                                                          or "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id = :role_parent_id_1
                                                                      UNION all
SELECT anon_1.role_id as role_id,
                                                                             anon_1.role_name as role_name,
                                                                             "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id as role_parent_id
                                                                      FROM   (SELECT "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id as role_id,
                                                                                     "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_name as role_name,
                                                                                     "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id as role_parent_id
                                                                              FROM   "TEMP__ALCHEMANCER_TYPES_RESOLVER"
                                                                              WHERE  "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id = :role_id_1
                                                                                  or "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_parent_id = :role_parent_id_1) as anon_1 join "TEMP__ALCHEMANCER_TYPES_RESOLVER"
                                                                              ON "TEMP__ALCHEMANCER_TYPES_RESOLVER".role_id = anon_1.role_parent_id)
SELECT DISTINCT roles_base_cte.role_id,
                roles_base_cte.role_name,
                roles_base_cte.role_parent_id
FROM   roles_base_cte, (SELECT roles_base_cte.role_id as role_id,
                               roles_base_cte.role_name as role_name,
                               roles_base_cte.role_parent_id as role_parent_id
                        FROM   roles_base_cte) as anon_2
WHERE  anon_2.role_id = :role_id_2
    or anon_2.role_parent_id = :role_parent_id_2
    """,
}
