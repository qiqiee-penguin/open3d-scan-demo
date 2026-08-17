import copy
import os

import numpy as np
import open3d as o3d
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="3D Scan Demo",
    layout="wide"
)

st.title("3D 扫描数据处理 Demo")
st.caption("基于 Open3D 的点云预处理、配准与 Mesh 重建流程")


# =====================================================
# 显示单个点云
# =====================================================
def show_point_cloud(pcd):

    points = np.asarray(pcd.points)

    if len(points) > 30000:
        index = np.random.choice(
            len(points),
            30000,
            replace=False
        )
        points = points[index]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode="markers",
            marker=dict(size=1.5),
            name="Point Cloud"
        )
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(aspectmode="data")
    )

    return fig


# =====================================================
# 显示两份点云
# =====================================================
def show_registration(source, target, transformation):

    source_copy = copy.deepcopy(source)
    source_copy.transform(transformation)

    source_points = np.asarray(source_copy.points)
    target_points = np.asarray(target.points)

    if len(source_points) > 20000:
        index = np.random.choice(
            len(source_points),
            20000,
            replace=False
        )
        source_points = source_points[index]

    if len(target_points) > 20000:
        index = np.random.choice(
            len(target_points),
            20000,
            replace=False
        )
        target_points = target_points[index]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=source_points[:, 0],
            y=source_points[:, 1],
            z=source_points[:, 2],
            mode="markers",
            marker=dict(
                size=1.5,
                color="#F5A623"
            ),
            name="Source"
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=target_points[:, 0],
            y=target_points[:, 1],
            z=target_points[:, 2],
            mode="markers",
            marker=dict(
                size=1.5,
                color="#2496ED"
            ),
            name="Target"
        )
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(aspectmode="data")
    )

    return fig


# =====================================================
# 显示 Mesh
# =====================================================
def show_mesh(mesh):

    vertices = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)

    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=triangles[:, 0],
                j=triangles[:, 1],
                k=triangles[:, 2],
                opacity=1.0
            )
        ]
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(aspectmode="data")
    )

    return fig


# =====================================================
# 加载 ICP 官方数据
# =====================================================
data = o3d.data.DemoICPPointClouds()

source_raw = o3d.io.read_point_cloud(
    data.paths[0]
)

target_raw = o3d.io.read_point_cloud(
    data.paths[1]
)


# =====================================================
# ICP 初始变换
# =====================================================
trans_init = np.asarray([
    [0.862, 0.011, -0.507, 0.5],
    [-0.139, 0.967, -0.215, 0.7],
    [0.487, 0.255, 0.835, -1.4],
    [0.0, 0.0, 0.0, 1.0]
])


# =====================================================
# 左侧流程
# =====================================================
st.sidebar.title("扫描处理流程")

stage = st.sidebar.radio(
    "选择处理阶段",
    [
        "项目概览",
        "① 原始点云",
        "② 降采样与去噪",
        "③ ICP 配准前",
        "④ ICP 配准后",
        "⑤ Mesh 重建",
        "⑥ 扫描质量评价"
    ]
)


# =====================================================
# 项目概览
# =====================================================
if stage == "项目概览":


    st.subheader("Open3D 手持 3D 扫描数据处理 Demo")


    st.write(
        """
        本项目用于实践手持 3D 扫描软件的数据处理链路，
        基于 Python + Open3D，将扫描点云经过预处理、
        多视角配准和表面重建，最终生成可导出的三维 Mesh。
        """
    )


    st.divider()


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "点云处理",
        "198,835 → 26,321"
    )


    col2.metric(
        "ICP Fitness",
        "0.356"
    )


    col3.metric(
        "ICP RMSE",
        "0.0102"
    )


    st.subheader("处理流程")


    st.markdown(
        """
        **扫描数据**


        ↓


        **点云预处理**
        - Voxel Down Sampling
        - Statistical Outlier Removal


        ↓


        **多视角点云配准**
        - ICP Registration
        - Fitness / RMSE 评价


        ↓


        **表面重建**
        - Normal Estimation
        - Ball Pivoting
        - Triangle Mesh


        ↓


        **质量评价与模型导出**
        - 点云噪声
        - 配准质量
        - PLY 模型导出
        """
    )


    st.divider()


    st.subheader("产品思考")


    st.markdown(
        """
        手持 3D 扫描产品不仅需要完成数据采集，还需要解决：


        - **实时质量反馈**：当前扫描区域是否存在噪声、数据不足
        - **跟踪与配准**：多视角扫描过程中是否发生错位或跟踪丢失
        - **完整度提示**：哪些区域仍存在缺失，需要继续补扫
        - **重建质量**：Mesh 是否出现孔洞、毛刺等问题
        - **结果应用**：模型能否进一步用于编辑、测量或 3D 打印


        Demo 当前重点验证点云预处理、配准、重建与基础质量评价，
        不包含真实扫描硬件数据采集和工业级精度测量。
        """
    )


# =====================================================
# ① 原始点云
# =====================================================
elif stage == "① 原始点云":

    st.subheader("原始扫描数据")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "原始点云数量",
        f"{len(source_raw.points):,}"
    )

    col2.metric(
        "当前阶段",
        "扫描采集"
    )

    col3.metric(
        "数据类型",
        "Point Cloud"
    )

    st.plotly_chart(
        show_point_cloud(source_raw),
        use_container_width=True
    )

    st.info(
        "扫描设备采集得到大量具有 XYZ 空间坐标的离散点。"
    )


# =====================================================
# ② 降采样与去噪
# =====================================================
elif stage == "② 降采样与去噪":

    st.subheader("点云预处理")

    down_pcd = source_raw.voxel_down_sample(
        voxel_size=0.02
    )

    clean_pcd, ind = (
        down_pcd.remove_statistical_outlier(
            nb_neighbors=20,
            std_ratio=2.0
        )
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "原始点数",
        f"{len(source_raw.points):,}"
    )

    col2.metric(
        "降采样后",
        f"{len(down_pcd.points):,}"
    )

    col3.metric(
        "去噪后",
        f"{len(clean_pcd.points):,}"
    )

    st.plotly_chart(
        show_point_cloud(clean_pcd),
        use_container_width=True
    )

    st.success("点云预处理完成")

    st.markdown(
        """
        **处理说明**

        - Voxel Down Sampling：降低点云密度
        - Statistical Outlier Removal：过滤离群点
        - 目的：减少计算量并提高后续处理稳定性
        """
    )


# =====================================================
# ③ ICP 配准前
# =====================================================
elif stage == "③ ICP 配准前":

    st.subheader("多视角点云 — 配准前")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Source 点数",
        f"{len(source_raw.points):,}"
    )

    col2.metric(
        "Target 点数",
        f"{len(target_raw.points):,}"
    )

    col3.metric(
        "当前状态",
        "粗对齐"
    )

    st.plotly_chart(
        show_registration(
            source_raw,
            target_raw,
            trans_init
        ),
        use_container_width=True
    )

    st.warning(
        "黄色和蓝色分别代表两个扫描视角，当前局部区域仍存在错位。"
    )


# =====================================================
# ④ ICP 配准后
# =====================================================
elif stage == "④ ICP 配准后":

    st.subheader("ICP 精配准结果")

    threshold = 0.02

    result = (
        o3d.pipelines.registration.registration_icp(
            source_raw,
            target_raw,
            threshold,
            trans_init,
            o3d.pipelines.registration
            .TransformationEstimationPointToPoint()
        )
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Fitness",
        f"{result.fitness:.3f}"
    )

    col2.metric(
        "Inlier RMSE",
        f"{result.inlier_rmse:.4f}"
    )

    col3.metric(
        "对应点数量",
        f"{len(result.correspondence_set):,}"
    )

    st.plotly_chart(
        show_registration(
            source_raw,
            target_raw,
            result.transformation
        ),
        use_container_width=True
    )

    st.success("ICP 配准完成")

    st.markdown(
        """
        **结果理解**

        - Fitness：反映两份点云的有效匹配情况
        - Inlier RMSE：反映匹配点之间的空间误差
        - Transformation：最终计算得到的旋转和平移关系
        """
    )


# =====================================================
# ⑤ Mesh 重建
# =====================================================
elif stage == "⑤ Mesh 重建":

    st.subheader("Point Cloud → Triangle Mesh")

    # Open3D 官方 Bunny 模型
    bunny_data = o3d.data.BunnyMesh()

    original_mesh = o3d.io.read_triangle_mesh(
        bunny_data.path
    )

    original_mesh.compute_vertex_normals()

    # 从模型表面采样 5000 个点
    # 用来模拟扫描得到的点云
    pcd = original_mesh.sample_points_poisson_disk(
        number_of_points=5000
    )

    # 计算法线
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=0.02,
            max_nn=30
        )
    )

    pcd.orient_normals_consistent_tangent_plane(
        30
    )

    # Ball Pivoting 表面重建
    radii = [
        0.005,
        0.01,
        0.02,
        0.04
    ]

    mesh = (
        o3d.geometry.TriangleMesh
        .create_from_point_cloud_ball_pivoting(
            pcd,
            o3d.utility.DoubleVector(radii)
        )
    )

    mesh.compute_vertex_normals()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "输入点云",
        f"{len(pcd.points):,}"
    )

    col2.metric(
        "Mesh 顶点",
        f"{len(mesh.vertices):,}"
    )

    col3.metric(
        "三角面数量",
        f"{len(mesh.triangles):,}"
    )

    st.plotly_chart(
        show_mesh(mesh),
        use_container_width=True
    )

    st.success(
        "点云表面重建完成"
    )

    st.markdown(
        """
        **处理说明**

        - Point Cloud：离散的三维空间点
        - Normal：描述点附近表面的方向
        - Ball Pivoting：根据点之间的空间关系生成三角面
        - Triangle Mesh：使用大量三角形表达连续物体表面
        """
    )

    # 创建输出文件夹
    os.makedirs(
        "output",
        exist_ok=True
    )

    output_path = (
        "output/reconstructed_bunny.ply"
    )

    o3d.io.write_triangle_mesh(
        output_path,
        mesh
    )

    with open(
        output_path,
        "rb"
    ) as file:

        st.download_button(
            label="导出 PLY 模型",
            data=file,
            file_name="reconstructed_bunny.ply",
            mime="application/octet-stream"
        )


# =====================================================
# ⑥ 扫描质量评价
# =====================================================
elif stage == "⑥ 扫描质量评价":

    st.subheader("扫描质量评价")

    down_pcd = source_raw.voxel_down_sample(
        voxel_size=0.02
    )

    clean_pcd, ind = (
        down_pcd.remove_statistical_outlier(
            nb_neighbors=20,
            std_ratio=2.0
        )
    )

    outlier_rate = (
        (len(down_pcd.points) - len(clean_pcd.points))
        / len(down_pcd.points)
        * 100
    )

    threshold = 0.02

    result = (
        o3d.pipelines.registration.registration_icp(
            source_raw,
            target_raw,
            threshold,
            trans_init,
            o3d.pipelines.registration
            .TransformationEstimationPointToPoint()
        )
    )


    # -------------------------
    # 展示指标
    # -------------------------
    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "原始点数",
        f"{len(source_raw.points):,}"
    )


    col2.metric(
        "离群点比例",
        f"{outlier_rate:.1f}%"
    )


    col3.metric(
        "配准 Fitness",
        f"{result.fitness:.3f}"
    )


    col4.metric(
        "配准 RMSE",
        f"{result.inlier_rmse:.4f}"
    )


    st.divider()


    st.subheader("质量诊断")


    # -------------------------
    # 简单产品规则
    # 仅用于 Demo
    # -------------------------


    if outlier_rate < 5:
        st.success(
            "✓ 点云噪声水平较低"
        )
    else:
        st.warning(
            "⚠ 点云离群点较多，建议重新检查扫描距离或环境"
        )


    if result.fitness > 0.3:
        st.success(
            "✓ 当前视角具有可用于配准的重叠区域"
        )
    else:
        st.warning(
            "⚠ 两次扫描重叠区域不足，建议返回上一视角重新扫描"
        )


    if result.inlier_rmse < 0.02:
        st.success(
            "✓ 当前配准误差较低"
        )
    else:
        st.warning(
            "⚠ 配准误差较高，建议重新定位或增加扫描特征"
        )


    st.info(
        """
        Demo 中使用离群点比例、ICP Fitness 和 Inlier RMSE
        作为扫描质量的基础代理指标。


        实际扫描产品还需要结合完整度、点密度、跟踪状态、
        重建缺陷、尺度精度等维度建立更完整的质量评价体系。
        """
    )