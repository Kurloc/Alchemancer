from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.sql.functions import array_agg, coalesce, func

from alchemancer.ast_handler import AstHandler
from tests.fixtures.models.generic.user import User


def test_ast_functions_1():
    token = AstHandler().convert_ast_to_sqlalchemy_column(
        """
# amdql select / column string
array_agg(aggregate_order_by(User.id, coalesce(User.account_balance, 0).desc()))
        """,
        {  # since this is a library for webservices, the implementor of amdql will be able to provide their
            # functions they want to expose to users, there are also some defaults that are included.
            "aggregate_order_by": aggregate_order_by,
            "coalesce": coalesce,
            "array_agg": array_agg,
        },
    )
    assert (
        str(token)
        == "array_agg(user_account.id ORDER BY coalesce(user_account.account_balance, %(coalesce_1)s) DESC)"
    )


def test_ast_functions_2():
    token = AstHandler().convert_ast_to_sqlalchemy_column(
        """
# amdql select / column string
array_agg(aggregate_order_by(coalesce(User.account_balance, 0), coalesce(User.account_balance, 0).desc()))
        """,
        {  # since this is a library for webservices, the implementor of amdql will be able to provide their
            # functions they want to expose to users, there are also some defaults that are included.
            "aggregate_order_by": aggregate_order_by,
            "coalesce": coalesce,
            "array_agg": array_agg,
        },
    )
    assert (
        str(token)
        == "array_agg(coalesce(user_account.account_balance, %(coalesce_1)s) ORDER BY coalesce(user_account.account_balance, %(coalesce_2)s) DESC)"
    )


def test_ast_functions_3():
    token = AstHandler().convert_ast_to_sqlalchemy_column(
        "coalesce(coalesce(array_agg(aggregate_order_by(User.id, User.id.desc()), '0'), 0))",
        {
            "aggregate_order_by": aggregate_order_by,
            "coalesce": coalesce,
            "array_agg": array_agg,
        },
    )
    assert (
        str(token)
        == "coalesce(coalesce(array_agg(user_account.id ORDER BY user_account.id DESC, :param_1), :coalesce_1))"
    )


def test_ast_obj():
    assert type(User) is type(AstHandler().convert_ast_to_sqlalchemy_column("User", {}))


def test_ast_constant():
    assert 1 == AstHandler().convert_ast_to_sqlalchemy_column("1", {})


def test_ast_obj_field():
    assert User.id == AstHandler().convert_ast_to_sqlalchemy_column("User.id", {})


def test_ast_field_method_no_params():
    assert str(User.id.desc()) == str(
        AstHandler().convert_ast_to_sqlalchemy_column("User.id.desc()", {})
    )


def test_ast_function_no_params():
    assert str(coalesce()) == str(
        AstHandler().convert_ast_to_sqlalchemy_column("coalesce()", {"coalesce": coalesce})
    )


def test_ast_function_params():
    assert str(coalesce(1, 0)) == str(
        AstHandler().convert_ast_to_sqlalchemy_column("coalesce(1, 0)", {"coalesce": coalesce})
    )


def test_ast_function_with_function_params():
    assert str(coalesce(None, func.now())) == str(
        AstHandler().convert_ast_to_sqlalchemy_column(
            "coalesce(None, now())", {"coalesce": coalesce, "now": func.now}
        )
    )


def test_ast_function_with_function_params_zoo():
    assert str(coalesce(coalesce(None, func.now()), 0).desc()) == str(
        AstHandler().convert_ast_to_sqlalchemy_column(
            "coalesce(coalesce(None, now()), 0).desc()",
            {"coalesce": coalesce, "now": func.now},
        )
    )


def test_ast_function_with_function_params_zoo_giga():
    assert str(
        array_agg(
            aggregate_order_by(
                coalesce(User.account_balance, 0),
                coalesce(User.account_balance, 0).desc(),
            )
        )
    ) == str(
        AstHandler().convert_ast_to_sqlalchemy_column(
            "array_agg(aggregate_order_by(coalesce(User.account_balance, 0), coalesce(User.account_balance, 0).desc()))",
            {
                "coalesce": coalesce,
                "now": func.now,
                "aggregate_order_by": aggregate_order_by,
                "User": User,
                "array_agg": array_agg,
            },
        )
    )
