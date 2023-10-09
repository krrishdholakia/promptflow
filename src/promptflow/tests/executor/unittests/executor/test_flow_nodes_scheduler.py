from concurrent.futures import Future
from unittest.mock import MagicMock

import pytest

from promptflow._core.flow_execution_context import FlowExecutionContext
from promptflow.contracts.flow import Node
from promptflow.executor._dag_manager import DAGManager
from promptflow.executor._flow_nodes_scheduler import (
    DEFAULT_CONCURRENCY_BULK,
    DEFAULT_CONCURRENCY_FLOW,
    FlowNodesScheduler,
)


@pytest.mark.unittest
class TestFlowNodesScheduler:
    def setup_method(self):
        # Define mock objects and methods
        self.tools_manager = MagicMock()
        self.context = MagicMock(spec=FlowExecutionContext)
        self.scheduler = FlowNodesScheduler(self.tools_manager, {}, [], DEFAULT_CONCURRENCY_BULK, self.context)

    def test_maximun_concurrency(self):
        scheduler = FlowNodesScheduler(self.tools_manager, {}, [], 1000, self.context)
        assert scheduler._node_concurrency == DEFAULT_CONCURRENCY_FLOW

    def test_collect_outputs(self):
        future1 = Future()
        future1.set_result("output1")
        future2 = Future()
        future2.set_result("output2")

        node1 = MagicMock(spec=Node)
        node1.name = "node1"
        node2 = MagicMock(spec=Node)
        node2.name = "node2"
        self.scheduler.future_to_node = {future1: node1, future2: node2}

        completed_nodes_outputs = self.scheduler._collect_outputs([future1, future2])

        assert completed_nodes_outputs == {"node1": future1.result(), "node2": future2.result()}

    def test_bypass_nodes(self):
        executor = MagicMock()

        dag_manager = MagicMock(spec=DAGManager)
        node1 = MagicMock(spec=Node)
        node1.name = "node1"
        # The return value will be a list with one item for the first time.
        # Will be a list without item for the second time.
        dag_manager.pop_bypassable_nodes.side_effect = ([node1], [])
        self.scheduler.dag_manager = dag_manager
        self.scheduler._execute_nodes(executor)
        self.scheduler.context.bypass_node.assert_called_once_with(
            node1, dag_manager.get_bypassed_node_outputs.return_value
        )

    def test_submit_nodes(self):
        executor = MagicMock()

        dag_manager = MagicMock(spec=DAGManager)
        node1 = MagicMock(spec=Node)
        node1.name = "node1"
        dag_manager.pop_bypassable_nodes.return_value = []
        # The return value will be a list with one item for the first time.
        # Will be a list without item for the second time.
        dag_manager.pop_ready_nodes.return_value = [node1]
        self.scheduler.dag_manager = dag_manager
        self.scheduler._execute_nodes(executor)
        self.scheduler.context.bypass_node.assert_not_called()
        assert node1 in self.scheduler.future_to_node.values()

    def test_future_cancelled(self):
        dag_manager = MagicMock(spec=DAGManager)
        self.scheduler.dag_manager = dag_manager
        dag_manager.completed.return_value = False
        dag_manager.pop_bypassable_nodes.return_value = []
        dag_manager.pop_ready_nodes.return_value = []

        failed_future = Future()
        failed_future.set_exception(Exception("test"))
        from concurrent.futures._base import CANCELLED, FINISHED

        failed_future._state = FINISHED
        cancelled_future = Future()

        node1 = MagicMock(spec=Node)
        node1.name = "node1"
        node2 = MagicMock(spec=Node)
        node2.name = "node2"
        self.scheduler.future_to_node = {failed_future: node1, cancelled_future: node2}
        try:
            self.scheduler.execute()
        except Exception:
            pass

        # Assert another future is cancelled.
        assert CANCELLED in cancelled_future._state
