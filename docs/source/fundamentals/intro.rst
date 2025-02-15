.. _intro:

LineaPy 101
===========

What is LineaPy?
----------------

LineaPy is a Python package for capturing, analyzing, and automating data science workflows.
At a high level, LineaPy traces the sequence of code execution to form a comprehensive understanding
of the code and its context. This understanding allows LineaPy to provide a set of tools that help
data scientists bring their work to production more quickly and easily, with just *two lines* of code.

Why Use LineaPy?
----------------

Going from data science development to production is full of friction. The engineering process to make messy development code production-ready is manual and
time-consuming. LineaPy creates a frictionless path for taking your data science work from development to production with just **two lines** of code.

Use Case 1: Cleaning Messy Notebooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working in a Jupyter notebook day-to-day, it is easy to write messy code by
jumping around between cells, deleting cells, editing cells, and executing the same cell multiple times - 
until we think we have some good results (e.g., tables, models, charts).
With this highly dynamic and interactive nature of notebook use, some issues may arise. For instance,
our colleagues who try to rerun the notebook may not be able to reproduce our results. Worse, with time passing,
we ourselves may have forgotten the exact steps to produce the previous results, hence unable to help our
colleagues.

One way to deal with this problem is to keep the notebook in sequential operations by constantly re-executing
the entire notebook during development. However, we soon realize that this interrupts our natural workflows and stream of
thoughts, decreasing our productivity. Therefore, it is much more common to clean up the notebook after development. This is a very time-consuming process and is not immune from reproducibility issues caused by deleting cells and out-of-order cell executions.

.. note::

    To see how LineaPy can help here, check out `cleaning up a messy notebook <https://github.com/LineaLabs/lineapy/blob/v0.2.x/.colab/clean_up_a_messy_notebook/clean_up_a_messy_notebook.ipynb>`_ demo.

Use Case 2: Revisiting Previous Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data science is often a team effort where one person's work uses results from another's. For instance,
a data scientist building a model may use various features engineered by other colleagues.
In using results generated by other people, we may encounter issues such as missing values, numbers that
look suspicious, and unintelligible variable names. If so, we may need to check how
these results came into being in the first place. Often, this means tracing back the code that was used
to generate the result in question (e.g., feature table). In practice, this can become a challenging task
because it may not be clear who produced the result. Even if we knew who to ask, the person might not remember
where the exact version of the code is. Worse, the person may have overwritten the code without version control.
Or, the person may no longer be in the organization with no proper handover of the relevant knowledge.
In any of these cases, it becomes extremely difficult to identify the root of the issue, which may render the result
unreliable and even unusable.

.. note::

    To see how LineaPy can help here, check out `discovering and tracing past work <https://github.com/LineaLabs/lineapy/blob/v0.2.x/.colab/discover_and_trace_past_work/discover_and_trace_past_work.ipynb>`_ demo.

Use Case 3: Building Pipelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As our notebooks become more mature, they may get used like pipelines. For instance, our notebook might process the
latest data to update dashboards. Or, it may pre-process data and dump it to the filesystem for downstream model development.
Since other people rely on up-to-date results from our work, we might be expected to re-execute these processes on a regular basis.
Running a notebook is a manual, brittle process prone to errors, so we may want to set up proper pipelines for production.
Relevant engineering support may not be available, so we may need to clean up and refactor the notebook code so it can be used in
orchestration systems or job schedulers (e.g., cron, Apache Airflow, Prefect). Of course, this is assuming that we already know
what they are and how to work with them. If not, we need to spend time learning about them in the first place.
All this operational work involves time-consuming, manual labor, which means less time for us to spend on our core duties as a data scientist.

.. note::

    To see how LineaPy can help here, check out `creating pipelines <https://github.com/LineaLabs/lineapy/blob/v0.2.x/.colab/create_a_simple_pipeline/create_a_simple_pipeline.ipynb>`_ demo.
