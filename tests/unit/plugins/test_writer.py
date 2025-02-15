import pickle
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writers import PipelineWriterFactory
from lineapy.plugins.utils import slugify
from lineapy.utils.utils import get_system_python_version, prettify


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, framework, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
            "script_pipeline_a0_b0",
            {},
            {},
            [],
            id="script_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a0_b0",
            {},
            {},
            [],
            id="airflow_pipeline_a0_b0",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a_b0_inputpar",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            ["b0"],
            id="airflow_pipeline_a_b0_input_parameter_per_artifact",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a_b0_inputpar_session",
            {},
            {"dag_flavor": "PythonOperatorPerSession"},
            ["b0"],
            id="airflow_pipeline_a_b0_input_parameter_per_session",
        ),
        pytest.param(
            "simple_twovar",
            "",
            ["pn"],
            "AIRFLOW",
            "airflow_pipeline_two_input_parameter",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            ["n", "p"],
            id="airflow_pipeline_two_input_parameter",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "SCRIPT",
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "AIRFLOW",
            "airflow_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            {},
            [],
            id="airflow_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "SCRIPT",
            "script_pipeline_housing_simple",
            {},
            {},
            [],
            id="script_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["p value"],
            "AIRFLOW",
            "airflow_pipeline_housing_simple",
            {},
            {},
            [],
            id="airflow_pipeline_housing_simple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "SCRIPT",
            "script_pipeline_housing_multiple",
            {},
            {},
            [],
            id="script_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "AIRFLOW",
            "airflow_pipeline_housing_multiple",
            {},
            {},
            [],
            id="airflow_pipeline_housing_multiple",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "SCRIPT",
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="script_pipeline_housing_w_dependencies",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "AIRFLOW",
            "airflow_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="airflow_pipeline_housing_w_dependencies",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "AIRFLOW",
            "airflow_complex_h_perart",
            {},
            {"dag_flavor": "PythonOperatorPerArtifact"},
            [],
            id="airflow_complex_h_perartifact",
        ),
        pytest.param(
            "simple",
            "",
            ["a", "b0"],
            "DVC",
            "dvc_pipeline_a_b0_singlestageallsessions",
            {},
            {"dag_flavor": "SingleStageAllSessions"},
            [],
            id="dvc_pipeline_a_b0_single_stage_all_sessions",
        ),
    ],
)
def test_pipeline_generation(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    framework,
    pipeline_name,
    dependencies,
    dag_config,
    input_parameters,
):
    """
    Test two sessions
    """

    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        execute(code2, snapshot=False)

    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db, artifact_def_list, input_parameters=input_parameters
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType[framework],
        artifact_collection=artifact_collection,
        dependencies=dependencies,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )

    # Write out pipeline files
    pipeline_writer.write_pipeline_files()

    # Get list of files to compare
    file_endings = ["_module.py", "_requirements.txt", "_Dockerfile"]
    if framework == "AIRFLOW":
        file_endings.append("_dag.py")

    file_names = [pipeline_name + file_suffix for file_suffix in file_endings]
    if framework == "DVC":
        file_names.append("dvc.yaml")

    # Compare generated vs. expected
    for expected_file_name in file_names:
        path = Path(tmp_path, expected_file_name)
        generated = path.read_text()
        path_expected = Path(
            "tests",
            "unit",
            "plugins",
            "expected",
            pipeline_name,
            expected_file_name,
        )

        if expected_file_name.endswith("_requirements.txt"):
            assert check_requirements_txt(generated, path_expected.read_text())
        else:
            to_compare = path_expected.read_text()
            if expected_file_name.endswith("_Dockerfile"):
                to_compare = to_compare.format(
                    python_version=get_system_python_version()
                )
            if expected_file_name.endswith(".py"):
                to_compare = prettify(to_compare)
            assert generated == to_compare


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "script_complex_h_perart",
            {},
            id="script_complex_h_perart",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            id="script_pipeline_housing_w_dependencies",
        ),
    ],
)
def test_pipeline_test_generation(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
):
    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        execute(code2, snapshot=False)

    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(linea_db, artifact_def_list)

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType["SCRIPT"],
        artifact_collection=artifact_collection,
        dependencies=dependencies,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        generate_test=True,
    )

    # Write out pipeline files
    pipeline_writer.write_pipeline_files()

    # Compare generated vs. expected
    path_generated = Path(tmp_path, f"test_{pipeline_name}.py")
    content_generated = path_generated.read_text()
    path_expected = Path(
        "tests",
        "unit",
        "plugins",
        "expected",
        pipeline_name,
        f"test_{pipeline_name}.py",
    )
    content_expected = prettify(path_expected.read_text())
    assert content_generated == content_expected

    # Check if artifact values have been (re-)stored
    # to serve as "ground truths" for pipeline testing
    for artname in artifact_list:
        path_generated = Path(
            tmp_path, "sample_output", f"{slugify(artname)}.pkl"
        )
        path_expected = Path(
            "tests",
            "unit",
            "plugins",
            "expected",
            pipeline_name,
            "sample_output",
            f"{slugify(artname)}.pkl",
        )
        with path_generated.open("rb") as fp:
            content_generated = pickle.load(fp)
        with path_expected.open("rb") as fp:
            content_expected = pickle.load(fp)
        assert type(content_generated) == type(content_expected)
