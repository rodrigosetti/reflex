from typing import Any, Dict, List, Type

import pytest

import reflex as rx
from reflex.base import Base
from reflex.compiler.compiler import compile_components
from reflex.components.base.bare import Bare
from reflex.components.chakra.layout.box import Box
from reflex.components.component import (
    Component,
    CustomComponent,
    StatefulComponent,
    custom_component,
)
from reflex.constants import EventTriggers
from reflex.event import EventChain, EventHandler
from reflex.state import BaseState
from reflex.style import Style
from reflex.utils import imports
from reflex.utils.imports import ImportVar
from reflex.vars import Var, VarData


@pytest.fixture
def test_state():
    class TestState(BaseState):
        num: int

        def do_something(self):
            pass

        def do_something_arg(self, arg):
            pass

    return TestState


@pytest.fixture
def component1() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent1(Component):
        # A test string prop.
        text: Var[str]

        # A test number prop.
        number: Var[int]

        def _get_imports(self) -> imports.ImportDict:
            return {"react": [ImportVar(tag="Component")]}

        def _get_custom_code(self) -> str:
            return "console.log('component1')"

    return TestComponent1


@pytest.fixture
def component2() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent2(Component):
        # A test list prop.
        arr: Var[List[str]]

        def get_event_triggers(self) -> Dict[str, Any]:
            """Test controlled triggers.

            Returns:
                Test controlled triggers.
            """
            return {
                **super().get_event_triggers(),
                "on_open": lambda e0: [e0],
                "on_close": lambda e0: [e0],
            }

        def _get_imports(self) -> imports.ImportDict:
            return {"react-redux": [ImportVar(tag="connect")]}

        def _get_custom_code(self) -> str:
            return "console.log('component2')"

    return TestComponent2


@pytest.fixture
def component3() -> Type[Component]:
    """A test component with hook defined.

    Returns:
        A test component.
    """

    class TestComponent3(Component):
        def _get_hooks(self) -> str:
            return "const a = () => true"

    return TestComponent3


@pytest.fixture
def component4() -> Type[Component]:
    """A test component with hook defined.

    Returns:
        A test component.
    """

    class TestComponent4(Component):
        def _get_hooks(self) -> str:
            return "const b = () => false"

    return TestComponent4


@pytest.fixture
def component5() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent5(Component):
        tag = "RandomComponent"

        _invalid_children: List[str] = ["Text"]

        _valid_children: List[str] = ["Text"]

        _valid_parents: List[str] = ["Text"]

    return TestComponent5


@pytest.fixture
def component6() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent6(Component):
        tag = "RandomComponent"

        _invalid_children: List[str] = ["Text"]

    return TestComponent6


@pytest.fixture
def component7() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent7(Component):
        tag = "RandomComponent"

        _valid_children: List[str] = ["Text"]

    return TestComponent7


@pytest.fixture
def on_click1() -> EventHandler:
    """A sample on click function.

    Returns:
        A sample on click function.
    """

    def on_click1():
        pass

    return EventHandler(fn=on_click1)


@pytest.fixture
def on_click2() -> EventHandler:
    """A sample on click function.

    Returns:
        A sample on click function.
    """

    def on_click2():
        pass

    return EventHandler(fn=on_click2)


@pytest.fixture
def my_component():
    """A test component function.

    Returns:
        A test component function.
    """

    def my_component(prop1: Var[str], prop2: Var[int]):
        return Box.create(prop1, prop2)

    return my_component


def test_set_style_attrs(component1):
    """Test that style attributes are set in the dict.

    Args:
        component1: A test component.
    """
    component = component1(color="white", text_align="center")
    assert component.style["color"] == "white"
    assert component.style["textAlign"] == "center"


def test_custom_attrs(component1):
    """Test that custom attributes are set in the dict.

    Args:
        component1: A test component.
    """
    component = component1(custom_attrs={"attr1": "1", "attr2": "attr2"})
    assert component.custom_attrs == {"attr1": "1", "attr2": "attr2"}


def test_create_component(component1):
    """Test that the component is created correctly.

    Args:
        component1: A test component.
    """
    children = [component1() for _ in range(3)]
    attrs = {"color": "white", "text_align": "center"}
    c = component1.create(*children, **attrs)
    assert isinstance(c, component1)
    assert c.children == children
    assert c.style == {"color": "white", "textAlign": "center"}


def test_add_style(component1, component2):
    """Test adding a style to a component.

    Args:
        component1: A test component.
        component2: A test component.
    """
    style = {
        component1: Style({"color": "white"}),
        component2: Style({"color": "black"}),
    }
    c1 = component1()._add_style_recursive(style)  # type: ignore
    c2 = component2()._add_style_recursive(style)  # type: ignore
    assert c1.style["color"] == "white"
    assert c2.style["color"] == "black"


def test_add_style_create(component1, component2):
    """Test that adding style works with the create method.

    Args:
        component1: A test component.
        component2: A test component.
    """
    style = {
        component1.create: Style({"color": "white"}),
        component2.create: Style({"color": "black"}),
    }
    c1 = component1()._add_style_recursive(style)  # type: ignore
    c2 = component2()._add_style_recursive(style)  # type: ignore
    assert c1.style["color"] == "white"
    assert c2.style["color"] == "black"


def test_get_imports(component1, component2):
    """Test getting the imports of a component.

    Args:
        component1: A test component.
        component2: A test component.
    """
    c1 = component1.create()
    c2 = component2.create(c1)
    assert c1._get_all_imports() == {"react": [ImportVar(tag="Component")]}
    assert c2._get_all_imports() == {
        "react-redux": [ImportVar(tag="connect")],
        "react": [ImportVar(tag="Component")],
    }


def test_get_custom_code(component1, component2):
    """Test getting the custom code of a component.

    Args:
        component1: A test component.
        component2: A test component.
    """
    # Check that the code gets compiled correctly.
    c1 = component1.create()
    c2 = component2.create()
    assert c1._get_all_custom_code() == {"console.log('component1')"}
    assert c2._get_all_custom_code() == {"console.log('component2')"}

    # Check that nesting components compiles both codes.
    c1 = component1.create(c2)
    assert c1._get_all_custom_code() == {
        "console.log('component1')",
        "console.log('component2')",
    }

    # Check that code is not duplicated.
    c1 = component1.create(c2, c2, c1, c1)
    assert c1._get_all_custom_code() == {
        "console.log('component1')",
        "console.log('component2')",
    }


def test_get_props(component1, component2):
    """Test that the props are set correctly.

    Args:
        component1: A test component.
        component2: A test component.
    """
    assert component1.get_props() == {"text", "number"}
    assert component2.get_props() == {"arr"}


@pytest.mark.parametrize(
    "text,number",
    [
        ("", 0),
        ("test", 1),
        ("hi", -13),
    ],
)
def test_valid_props(component1, text: str, number: int):
    """Test that we can construct a component with valid props.

    Args:
        component1: A test component.
        text: A test string.
        number: A test number.
    """
    c = component1.create(text=text, number=number)
    assert c.text._decode() == text
    assert c.number._decode() == number


@pytest.mark.parametrize(
    "text,number", [("", "bad_string"), (13, 1), ("test", [1, 2, 3])]
)
def test_invalid_prop_type(component1, text: str, number: int):
    """Test that an invalid prop type raises an error.

    Args:
        component1: A test component.
        text: A test string.
        number: A test number.
    """
    # Check that
    with pytest.raises(TypeError):
        component1.create(text=text, number=number)


def test_var_props(component1, test_state):
    """Test that we can set a Var prop.

    Args:
        component1: A test component.
        test_state: A test state.
    """
    c1 = component1.create(text="hello", number=test_state.num)
    assert c1.number.equals(test_state.num)


def test_get_event_triggers(component1, component2):
    """Test that we can get the triggers of a component.

    Args:
        component1: A test component.
        component2: A test component.
    """
    default_triggers = {
        EventTriggers.ON_FOCUS,
        EventTriggers.ON_BLUR,
        EventTriggers.ON_CLICK,
        EventTriggers.ON_CONTEXT_MENU,
        EventTriggers.ON_DOUBLE_CLICK,
        EventTriggers.ON_MOUSE_DOWN,
        EventTriggers.ON_MOUSE_ENTER,
        EventTriggers.ON_MOUSE_LEAVE,
        EventTriggers.ON_MOUSE_MOVE,
        EventTriggers.ON_MOUSE_OUT,
        EventTriggers.ON_MOUSE_OVER,
        EventTriggers.ON_MOUSE_UP,
        EventTriggers.ON_SCROLL,
        EventTriggers.ON_MOUNT,
        EventTriggers.ON_UNMOUNT,
    }
    assert set(component1().get_event_triggers().keys()) == default_triggers
    assert (
        component2().get_event_triggers().keys()
        == {"on_open", "on_close"} | default_triggers
    )


@pytest.fixture
def test_component() -> Type[Component]:
    """A test component.

    Returns:
        A test component.
    """

    class TestComponent(Component):
        pass

    return TestComponent


# Write a test case to check if the create method filters out None props
def test_create_filters_none_props(test_component):
    child1 = test_component()
    child2 = test_component()
    props = {
        "prop1": "value1",
        "prop2": None,
        "prop3": "value3",
        "prop4": None,
        "style": {"color": "white", "text-align": "center"},  # Adding a style prop
    }

    component = test_component.create(child1, child2, **props)

    # Assert that None props are not present in the component's props
    assert "prop2" not in component.get_props()
    assert "prop4" not in component.get_props()

    # Assert that the style prop is present in the component's props
    assert component.style["color"] == "white"
    assert component.style["text-align"] == "center"


class C1State(BaseState):
    """State for testing C1 component."""

    def mock_handler(self, _e, _bravo, _charlie):
        """Mock handler."""
        pass


def test_component_event_trigger_arbitrary_args():
    """Test that we can define arbitrary types for the args of an event trigger."""

    class Obj(Base):
        custom: int = 0

    def on_foo_spec(_e, alpha: str, bravo: Dict[str, Any], charlie: Obj):
        return [_e.target.value, bravo["nested"], charlie.custom + 42]

    class C1(Component):
        library = "/local"
        tag = "C1"

        def get_event_triggers(self) -> Dict[str, Any]:
            return {
                **super().get_event_triggers(),
                "on_foo": on_foo_spec,
            }

    comp = C1.create(on_foo=C1State.mock_handler)

    assert comp.render()["props"][0] == (
        "onFoo={(__e,_alpha,_bravo,_charlie) => addEvents("
        '[Event("c1_state.mock_handler", {_e:__e.target.value,_bravo:_bravo["nested"],_charlie:((_charlie.custom) + (42))})], '
        "(__e,_alpha,_bravo,_charlie), {})}"
    )


def test_create_custom_component(my_component):
    """Test that we can create a custom component.

    Args:
        my_component: A test custom component.
    """
    component = CustomComponent(component_fn=my_component, prop1="test", prop2=1)
    assert component.tag == "MyComponent"
    assert component.get_props() == set()
    assert component._get_all_custom_components() == {component}


def test_custom_component_hash(my_component):
    """Test that the hash of a custom component is correct.

    Args:
        my_component: A test custom component.
    """
    component1 = CustomComponent(component_fn=my_component, prop1="test", prop2=1)
    component2 = CustomComponent(component_fn=my_component, prop1="test", prop2=2)
    assert {component1, component2} == {component1}


def test_custom_component_wrapper():
    """Test that the wrapper of a custom component is correct."""

    @custom_component
    def my_component(width: Var[int], color: Var[str]):
        return rx.box(
            width=width,
            color=color,
        )

    from reflex.components.radix.themes.typography.text import Text

    ccomponent = my_component(
        rx.text("child"), width=Var.create(1), color=Var.create("red")
    )
    assert isinstance(ccomponent, CustomComponent)
    assert len(ccomponent.children) == 1
    assert isinstance(ccomponent.children[0], Text)

    component = ccomponent.get_component(ccomponent)
    assert isinstance(component, Box)


def test_invalid_event_handler_args(component2, test_state):
    """Test that an invalid event handler raises an error.

    Args:
        component2: A test component.
        test_state: A test state.
    """
    # Uncontrolled event handlers should not take args.
    # This is okay.
    component2.create(on_click=test_state.do_something)
    # This is not okay.
    with pytest.raises(ValueError):
        component2.create(on_click=test_state.do_something_arg)
        component2.create(on_open=test_state.do_something)
        component2.create(
            on_open=[test_state.do_something_arg, test_state.do_something]
        )
    # However lambdas are okay.
    component2.create(on_click=lambda: test_state.do_something_arg(1))
    component2.create(
        on_click=lambda: [test_state.do_something_arg(1), test_state.do_something]
    )
    component2.create(
        on_click=lambda: [test_state.do_something_arg(1), test_state.do_something()]
    )

    # Controlled event handlers should take args.
    # This is okay.
    component2.create(on_open=test_state.do_something_arg)


def test_get_hooks_nested(component1, component2, component3):
    """Test that a component returns hooks from child components.

    Args:
        component1: test component.
        component2: another component.
        component3: component with hooks defined.
    """
    c = component1.create(
        component2.create(arr=[]),
        component3.create(),
        component3.create(),
        component3.create(),
        text="a",
        number=1,
    )
    assert c._get_all_hooks() == component3()._get_all_hooks()


def test_get_hooks_nested2(component3, component4):
    """Test that a component returns both when parent and child have hooks.

    Args:
        component3: component with hooks defined.
        component4: component with different hooks defined.
    """
    exp_hooks = {**component3()._get_all_hooks(), **component4()._get_all_hooks()}
    assert component3.create(component4.create())._get_all_hooks() == exp_hooks
    assert component4.create(component3.create())._get_all_hooks() == exp_hooks
    assert (
        component4.create(
            component3.create(),
            component4.create(),
            component3.create(),
        )._get_all_hooks()
        == exp_hooks
    )


@pytest.mark.parametrize("fixture", ["component5", "component6"])
def test_unsupported_child_components(fixture, request):
    """Test that a value error is raised when an unsupported component (a child component found in the
    component's invalid children list) is provided as a child.

    Args:
        fixture: the test component as a fixture.
        request: Pytest request.
    """
    component = request.getfixturevalue(fixture)
    with pytest.raises(ValueError) as err:
        comp = component.create(rx.text("testing component"))
        comp.render()
    assert (
        err.value.args[0]
        == f"The component `{component.__name__}` cannot have `Text` as a child component"
    )


def test_unsupported_parent_components(component5):
    """Test that a value error is raised when an component is not in _valid_parents of one of its children.

    Args:
        component5: component with valid parent of "Text" only
    """
    with pytest.raises(ValueError) as err:
        rx.box(component5.create())
    assert (
        err.value.args[0]
        == f"The component `{component5.__name__}` can only be a child of the components: `{component5._valid_parents[0]}`. Got `Box` instead."
    )


@pytest.mark.parametrize("fixture", ["component5", "component7"])
def test_component_with_only_valid_children(fixture, request):
    """Test that a value error is raised when an unsupported component (a child component not found in the
    component's valid children list) is provided as a child.

    Args:
        fixture: the test component as a fixture.
        request: Pytest request.
    """
    component = request.getfixturevalue(fixture)
    with pytest.raises(ValueError) as err:
        comp = component.create(rx.box("testing component"))
        comp.render()
    assert (
        err.value.args[0]
        == f"The component `{component.__name__}` only allows the components: `Text` as children. "
        f"Got `Box` instead."
    )


@pytest.mark.parametrize(
    "component,rendered",
    [
        (rx.text("hi"), "<RadixThemesText as={`p`}>\n  {`hi`}\n</RadixThemesText>"),
        (
            rx.box(rx.chakra.heading("test", size="md")),
            "<RadixThemesBox>\n  <Heading size={`md`}>\n  {`test`}\n</Heading>\n</RadixThemesBox>",
        ),
    ],
)
def test_format_component(component, rendered):
    """Test that a component is formatted correctly.

    Args:
        component: The component to format.
        rendered: The expected rendered component.
    """
    assert str(component) == rendered


def test_stateful_component(test_state):
    """Test that a stateful component is created correctly.

    Args:
        test_state: A test state.
    """
    text_component = rx.text(test_state.num)
    stateful_component = StatefulComponent.compile_from(text_component)
    assert isinstance(stateful_component, StatefulComponent)
    assert stateful_component.tag is not None
    assert stateful_component.tag.startswith("Text_")
    assert stateful_component.references == 1
    sc2 = StatefulComponent.compile_from(rx.text(test_state.num))
    assert isinstance(sc2, StatefulComponent)
    assert stateful_component.references == 2
    assert sc2.references == 2


def test_stateful_component_memoize_event_trigger(test_state):
    """Test that a stateful component is created correctly with events.

    Args:
        test_state: A test state.
    """
    button_component = rx.button("Click me", on_click=test_state.do_something)
    stateful_component = StatefulComponent.compile_from(button_component)
    assert isinstance(stateful_component, StatefulComponent)

    # No event trigger? No StatefulComponent
    assert not isinstance(
        StatefulComponent.compile_from(rx.button("Click me")), StatefulComponent
    )


def test_stateful_banner():
    """Test that a stateful component is created correctly with events."""
    connection_modal_component = rx.connection_modal()
    stateful_component = StatefulComponent.compile_from(connection_modal_component)
    assert isinstance(stateful_component, StatefulComponent)


TEST_VAR = Var.create_safe("test")._replace(
    merge_var_data=VarData(
        hooks={"useTest": None},
        imports={"test": {ImportVar(tag="test")}},
        state="Test",
        interpolations=[],
    )
)
FORMATTED_TEST_VAR = Var.create(f"foo{TEST_VAR}bar")
STYLE_VAR = TEST_VAR._replace(_var_name="style", _var_is_local=False)
EVENT_CHAIN_VAR = TEST_VAR._replace(_var_type=EventChain)
ARG_VAR = Var.create("arg")

TEST_VAR_DICT_OF_DICT = Var.create_safe({"a": {"b": "test"}})._replace(
    merge_var_data=TEST_VAR._var_data
)
FORMATTED_TEST_VAR_DICT_OF_DICT = Var.create_safe({"a": {"b": f"footestbar"}})._replace(
    merge_var_data=TEST_VAR._var_data
)

TEST_VAR_LIST_OF_LIST = Var.create_safe([["test"]])._replace(
    merge_var_data=TEST_VAR._var_data
)
FORMATTED_TEST_VAR_LIST_OF_LIST = Var.create_safe([["footestbar"]])._replace(
    merge_var_data=TEST_VAR._var_data
)

TEST_VAR_LIST_OF_LIST_OF_LIST = Var.create_safe([[["test"]]])._replace(
    merge_var_data=TEST_VAR._var_data
)
FORMATTED_TEST_VAR_LIST_OF_LIST_OF_LIST = Var.create_safe([[["footestbar"]]])._replace(
    merge_var_data=TEST_VAR._var_data
)

TEST_VAR_LIST_OF_DICT = Var.create_safe([{"a": "test"}])._replace(
    merge_var_data=TEST_VAR._var_data
)
FORMATTED_TEST_VAR_LIST_OF_DICT = Var.create_safe([{"a": "footestbar"}])._replace(
    merge_var_data=TEST_VAR._var_data
)


class ComponentNestedVar(Component):
    """A component with nested Var types."""

    dict_of_dict: Var[Dict[str, Dict[str, str]]]
    list_of_list: Var[List[List[str]]]
    list_of_list_of_list: Var[List[List[List[str]]]]
    list_of_dict: Var[List[Dict[str, str]]]


class EventState(rx.State):
    """State for testing event handlers with _get_vars."""

    v: int = 42

    def handler(self):
        """A handler that does nothing."""

    def handler2(self, arg):
        """A handler that takes an arg.

        Args:
            arg: An arg.
        """


@pytest.mark.parametrize(
    ("component", "exp_vars"),
    (
        pytest.param(
            Bare.create(TEST_VAR),
            [TEST_VAR],
            id="direct-bare",
        ),
        pytest.param(
            Bare.create(f"foo{TEST_VAR}bar"),
            [FORMATTED_TEST_VAR],
            id="fstring-bare",
        ),
        pytest.param(
            rx.text(as_=TEST_VAR),
            [TEST_VAR],
            id="direct-prop",
        ),
        pytest.param(
            rx.heading(as_=f"foo{TEST_VAR}bar"),
            [FORMATTED_TEST_VAR],
            id="fstring-prop",
        ),
        pytest.param(
            rx.fragment(id=TEST_VAR),
            [TEST_VAR],
            id="direct-id",
        ),
        pytest.param(
            rx.fragment(id=f"foo{TEST_VAR}bar"),
            [FORMATTED_TEST_VAR],
            id="fstring-id",
        ),
        pytest.param(
            rx.fragment(key=TEST_VAR),
            [TEST_VAR],
            id="direct-key",
        ),
        pytest.param(
            rx.fragment(key=f"foo{TEST_VAR}bar"),
            [FORMATTED_TEST_VAR],
            id="fstring-key",
        ),
        pytest.param(
            rx.fragment(class_name=TEST_VAR),
            [TEST_VAR],
            id="direct-class_name",
        ),
        pytest.param(
            rx.fragment(class_name=f"foo{TEST_VAR}bar"),
            [FORMATTED_TEST_VAR],
            id="fstring-class_name",
        ),
        pytest.param(
            rx.fragment(special_props={TEST_VAR}),
            [TEST_VAR],
            id="direct-special_props",
        ),
        pytest.param(
            rx.fragment(special_props={Var.create(f"foo{TEST_VAR}bar")}),
            [FORMATTED_TEST_VAR],
            id="fstring-special_props",
        ),
        pytest.param(
            # custom_attrs cannot accept a Var directly as a value
            rx.fragment(custom_attrs={"href": f"{TEST_VAR}"}),
            [TEST_VAR],
            id="fstring-custom_attrs-nofmt",
        ),
        pytest.param(
            rx.fragment(custom_attrs={"href": f"foo{TEST_VAR}bar"}),
            [FORMATTED_TEST_VAR],
            id="fstring-custom_attrs",
        ),
        pytest.param(
            rx.fragment(background_color=TEST_VAR),
            [STYLE_VAR],
            id="direct-background_color",
        ),
        pytest.param(
            rx.fragment(background_color=f"foo{TEST_VAR}bar"),
            [STYLE_VAR],
            id="fstring-background_color",
        ),
        pytest.param(
            rx.fragment(style={"background_color": TEST_VAR}),  # type: ignore
            [STYLE_VAR],
            id="direct-style-background_color",
        ),
        pytest.param(
            rx.fragment(style={"background_color": f"foo{TEST_VAR}bar"}),  # type: ignore
            [STYLE_VAR],
            id="fstring-style-background_color",
        ),
        pytest.param(
            rx.fragment(on_click=EVENT_CHAIN_VAR),  # type: ignore
            [EVENT_CHAIN_VAR],
            id="direct-event-chain",
        ),
        pytest.param(
            rx.fragment(on_click=EventState.handler),
            [],
            id="direct-event-handler",
        ),
        pytest.param(
            rx.fragment(on_click=EventState.handler2(TEST_VAR)),  # type: ignore
            [ARG_VAR, TEST_VAR],
            id="direct-event-handler-arg",
        ),
        pytest.param(
            rx.fragment(on_click=EventState.handler2(EventState.v)),  # type: ignore
            [ARG_VAR, EventState.v],
            id="direct-event-handler-arg2",
        ),
        pytest.param(
            rx.fragment(on_click=lambda: EventState.handler2(TEST_VAR)),  # type: ignore
            [ARG_VAR, TEST_VAR],
            id="direct-event-handler-lambda",
        ),
        pytest.param(
            ComponentNestedVar.create(dict_of_dict={"a": {"b": TEST_VAR}}),
            [TEST_VAR_DICT_OF_DICT],
            id="direct-dict_of_dict",
        ),
        pytest.param(
            ComponentNestedVar.create(dict_of_dict={"a": {"b": f"foo{TEST_VAR}bar"}}),
            [FORMATTED_TEST_VAR_DICT_OF_DICT],
            id="fstring-dict_of_dict",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_list=[[TEST_VAR]]),
            [TEST_VAR_LIST_OF_LIST],
            id="direct-list_of_list",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_list=[[f"foo{TEST_VAR}bar"]]),
            [FORMATTED_TEST_VAR_LIST_OF_LIST],
            id="fstring-list_of_list",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_list_of_list=[[[TEST_VAR]]]),
            [TEST_VAR_LIST_OF_LIST_OF_LIST],
            id="direct-list_of_list_of_list",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_list_of_list=[[[f"foo{TEST_VAR}bar"]]]),
            [FORMATTED_TEST_VAR_LIST_OF_LIST_OF_LIST],
            id="fstring-list_of_list_of_list",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_dict=[{"a": TEST_VAR}]),
            [TEST_VAR_LIST_OF_DICT],
            id="direct-list_of_dict",
        ),
        pytest.param(
            ComponentNestedVar.create(list_of_dict=[{"a": f"foo{TEST_VAR}bar"}]),
            [FORMATTED_TEST_VAR_LIST_OF_DICT],
            id="fstring-list_of_dict",
        ),
    ),
)
def test_get_vars(component, exp_vars):
    comp_vars = sorted(component._get_vars(), key=lambda v: v._var_name)
    assert len(comp_vars) == len(exp_vars)
    for comp_var, exp_var in zip(
        comp_vars,
        sorted(exp_vars, key=lambda v: v._var_name),
    ):
        assert comp_var.equals(exp_var)


def test_instantiate_all_components():
    """Test that all components can be instantiated."""
    # These components all have required arguments and cannot be trivially instantiated.
    untested_components = {
        "Card",
        "Cond",
        "DebounceInput",
        "Foreach",
        "FormControl",
        "Html",
        "Icon",
        "Match",
        "Markdown",
        "MultiSelect",
        "Option",
        "Popover",
        "Radio",
        "Script",
        "Tag",
        "Tfoot",
        "Thead",
    }
    for component_name in rx._ALL_COMPONENTS:  # type: ignore
        if component_name in untested_components:
            continue
        component = getattr(rx, component_name)
        if isinstance(component, type) and issubclass(component, Component):
            component.create()


class InvalidParentComponent(Component):
    """Invalid Parent Component."""

    ...


class ValidComponent1(Component):
    """Test valid component."""

    _valid_children = ["ValidComponent2"]


class ValidComponent2(Component):
    """Test valid component."""

    ...


class ValidComponent3(Component):
    """Test valid component."""

    _valid_parents = ["ValidComponent2"]


class ValidComponent4(Component):
    """Test valid component."""

    _invalid_children = ["InvalidComponent"]


class InvalidComponent(Component):
    """Test invalid component."""

    ...


valid_component1 = ValidComponent1.create
valid_component2 = ValidComponent2.create
invalid_component = InvalidComponent.create
valid_component3 = ValidComponent3.create
invalid_parent = InvalidParentComponent.create
valid_component4 = ValidComponent4.create


def test_validate_valid_children():
    valid_component1(valid_component2())
    valid_component1(
        rx.fragment(valid_component2()),
    )
    valid_component1(
        rx.fragment(
            rx.fragment(
                rx.fragment(valid_component2()),
            ),
        ),
    )

    valid_component1(
        rx.cond(  # type: ignore
            True,
            rx.fragment(valid_component2()),
            rx.fragment(
                rx.foreach(Var.create([1, 2, 3]), lambda x: valid_component2(x))  # type: ignore
            ),
        )
    )

    valid_component1(
        rx.cond(
            True,
            valid_component2(),
            rx.fragment(
                rx.match(
                    "condition",
                    ("first", valid_component2()),
                    rx.fragment(valid_component2(rx.text("default"))),
                )
            ),
        )
    )

    valid_component1(
        rx.match(
            "condition",
            ("first", valid_component2()),
            ("second", "third", rx.fragment(valid_component2())),
            (
                "fourth",
                rx.cond(True, valid_component2(), rx.fragment(valid_component2())),
            ),
            (
                "fifth",
                rx.match(
                    "nested_condition",
                    ("nested_first", valid_component2()),
                    rx.fragment(valid_component2()),
                ),
                valid_component2(),
            ),
        )
    )


def test_validate_valid_parents():
    valid_component2(valid_component3())
    valid_component2(
        rx.fragment(valid_component3()),
    )
    valid_component1(
        rx.fragment(
            valid_component2(
                rx.fragment(valid_component3()),
            ),
        ),
    )

    valid_component2(
        rx.cond(  # type: ignore
            True,
            rx.fragment(valid_component3()),
            rx.fragment(
                rx.foreach(
                    Var.create([1, 2, 3]),  # type: ignore
                    lambda x: valid_component2(valid_component3(x)),
                )
            ),
        )
    )

    valid_component2(
        rx.cond(
            True,
            valid_component3(),
            rx.fragment(
                rx.match(
                    "condition",
                    ("first", valid_component3()),
                    rx.fragment(valid_component3(rx.text("default"))),
                )
            ),
        )
    )

    valid_component2(
        rx.match(
            "condition",
            ("first", valid_component3()),
            ("second", "third", rx.fragment(valid_component3())),
            (
                "fourth",
                rx.cond(True, valid_component3(), rx.fragment(valid_component3())),
            ),
            (
                "fifth",
                rx.match(
                    "nested_condition",
                    ("nested_first", valid_component3()),
                    rx.fragment(valid_component3()),
                ),
                valid_component3(),
            ),
        )
    )


def test_validate_invalid_children():
    with pytest.raises(ValueError):
        valid_component4(invalid_component())

    with pytest.raises(ValueError):
        valid_component4(
            rx.fragment(invalid_component()),
        )

    with pytest.raises(ValueError):
        valid_component2(
            rx.fragment(
                valid_component4(
                    rx.fragment(invalid_component()),
                ),
            ),
        )

    with pytest.raises(ValueError):
        valid_component4(
            rx.cond(  # type: ignore
                True,
                rx.fragment(invalid_component()),
                rx.fragment(
                    rx.foreach(Var.create([1, 2, 3]), lambda x: invalid_component(x))  # type: ignore
                ),
            )
        )

    with pytest.raises(ValueError):
        valid_component4(
            rx.cond(
                True,
                invalid_component(),
                rx.fragment(
                    rx.match(
                        "condition",
                        ("first", invalid_component()),
                        rx.fragment(invalid_component(rx.text("default"))),
                    )
                ),
            )
        )

    with pytest.raises(ValueError):
        valid_component4(
            rx.match(
                "condition",
                ("first", invalid_component()),
                ("second", "third", rx.fragment(invalid_component())),
                (
                    "fourth",
                    rx.cond(True, invalid_component(), rx.fragment(valid_component2())),
                ),
                (
                    "fifth",
                    rx.match(
                        "nested_condition",
                        ("nested_first", invalid_component()),
                        rx.fragment(invalid_component()),
                    ),
                    invalid_component(),
                ),
            )
        )


def test_rename_props():
    """Test that _rename_props works and is inherited."""

    class C1(Component):
        tag = "C1"

        prop1: Var[str]
        prop2: Var[str]

        _rename_props = {"prop1": "renamed_prop1", "prop2": "renamed_prop2"}

    class C2(C1):
        tag = "C2"

        prop3: Var[str]

        _rename_props = {"prop2": "subclass_prop2", "prop3": "renamed_prop3"}

    c1 = C1.create(prop1="prop1_1", prop2="prop2_1")
    rendered_c1 = c1.render()
    assert "renamed_prop1={`prop1_1`}" in rendered_c1["props"]
    assert "renamed_prop2={`prop2_1`}" in rendered_c1["props"]

    c2 = C2.create(prop1="prop1_2", prop2="prop2_2", prop3="prop3_2")
    rendered_c2 = c2.render()
    assert "renamed_prop1={`prop1_2`}" in rendered_c2["props"]
    assert "subclass_prop2={`prop2_2`}" in rendered_c2["props"]
    assert "renamed_prop3={`prop3_2`}" in rendered_c2["props"]


def test_deprecated_props(capsys):
    """Assert that deprecated underscore suffix props are translated.

    Args:
        capsys: Pytest fixture for capturing stdout and stderr.
    """

    class C1(Component):
        tag = "C1"

        type: Var[str]
        min: Var[str]
        max: Var[str]

    # No warnings are emitted when using the new prop names.
    c1_1 = C1.create(type="type1", min="min1", max="max1")
    out_err = capsys.readouterr()
    assert not out_err.err
    assert not out_err.out

    c1_1_render = c1_1.render()
    assert "type={`type1`}" in c1_1_render["props"]
    assert "min={`min1`}" in c1_1_render["props"]
    assert "max={`max1`}" in c1_1_render["props"]

    # Deprecation warning is emitted with underscore suffix,
    # but the component still works.
    c1_2 = C1.create(type_="type2", min_="min2", max_="max2")
    out_err = capsys.readouterr()
    assert out_err.out.count("DeprecationWarning:") == 3
    assert not out_err.err

    c1_2_render = c1_2.render()
    assert "type={`type2`}" in c1_2_render["props"]
    assert "min={`min2`}" in c1_2_render["props"]
    assert "max={`max2`}" in c1_2_render["props"]

    class C2(Component):
        tag = "C2"

        type_: Var[str]
        min_: Var[str]
        max_: Var[str]

    # No warnings are emitted if the actual prop has an underscore suffix
    c2_1 = C2.create(type_="type1", min_="min1", max_="max1")
    out_err = capsys.readouterr()
    assert not out_err.err
    assert not out_err.out

    c2_1_render = c2_1.render()
    assert "type={`type1`}" in c2_1_render["props"]
    assert "min={`min1`}" in c2_1_render["props"]
    assert "max={`max1`}" in c2_1_render["props"]


def test_custom_component_get_imports():
    class Inner(Component):
        tag = "Inner"
        library = "inner"

    class Other(Component):
        tag = "Other"
        library = "other"

    @rx.memo
    def wrapper():
        return Inner.create()

    @rx.memo
    def outer(c: Component):
        return Other.create(c)

    custom_comp = wrapper()

    # Inner is not imported directly, but it is imported by the custom component.
    assert "inner" not in custom_comp._get_all_imports()

    # The imports are only resolved during compilation.
    _, _, imports_inner = compile_components(custom_comp._get_all_custom_components())
    assert "inner" in imports_inner

    outer_comp = outer(c=wrapper())

    # Libraries are not imported directly, but are imported by the custom component.
    assert "inner" not in outer_comp._get_all_imports()
    assert "other" not in outer_comp._get_all_imports()

    # The imports are only resolved during compilation.
    _, _, imports_outer = compile_components(outer_comp._get_all_custom_components())
    assert "inner" in imports_outer
    assert "other" in imports_outer


def test_custom_component_declare_event_handlers_in_fields():
    class ReferenceComponent(Component):
        def get_event_triggers(self) -> Dict[str, Any]:
            """Test controlled triggers.

            Returns:
                Test controlled triggers.
            """
            return {
                **super().get_event_triggers(),
                "on_a": lambda e: [e],
                "on_b": lambda e: [e.target.value],
                "on_c": lambda e: [],
                "on_d": lambda: [],
                "on_e": lambda: [],
            }

    class TestComponent(Component):
        on_a: EventHandler[lambda e0: [e0]]
        on_b: EventHandler[lambda e0: [e0.target.value]]
        on_c: EventHandler[lambda e0: []]
        on_d: EventHandler[lambda: []]
        on_e: EventHandler

    custom_component = ReferenceComponent.create()
    test_component = TestComponent.create()
    assert (
        custom_component.get_event_triggers().keys()
        == test_component.get_event_triggers().keys()
    )
