from pathlib import Path
import os
import hmac
import hashlib

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================= APP CONFIGURATION =============================
st.set_page_config(
    page_title="Road Accident Analysis",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "accidents.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "accident_id", "date", "location", "severity", "weather",
    "vehicles_involved", "injuries", "fatalities", "latitude", "longitude",
]

SEVERITY_OPTIONS = ["Low", "Medium", "High", "Critical", "Unknown"]
WEATHER_OPTIONS = ["Clear", "Rain", "Fog", "Cloudy", "Night", "Other", "Unknown"]

# Local demonstration credentials. Change these environment variables before
# sharing the app. For deployment, use Streamlit secrets and a proper auth setup.
DEFAULT_USERNAME = os.getenv("APP_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("APP_PASSWORD", "admin")



# --------------------------------- Styling -----------------------------------
st.markdown(
    """
    <style>
    /* Main page */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #F3F6FC !important;
        color: #172033 !important;
    }

    /* Main headings and text */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] label,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] {
        color: #172033 !important;
        opacity: 1 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
    }

    [data-testid="stSidebar"] * {
        color: #F9FAFB !important;
    }

    /* Input boxes */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        border: 1px solid #94A3B8 !important;
        border-radius: 8px !important;
    }

    /* Dropdowns and multiselect controls */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        border-color: #94A3B8 !important;
    }

    [data-testid="stSelectbox"] input,
    [data-testid="stMultiSelect"] input {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
    }

    /* Dropdown selected values */
    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stMultiSelect"] [data-baseweb="select"] * {
        color: #172033 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D8E1EF !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.06);
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #172033 !important;
        opacity: 1 !important;
    }

    /* Tables */
    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        border-radius: 10px !important;
    }

    /* Buttons */
    [data-testid="stMain"] .stButton button,
    [data-testid="stMain"] .stFormSubmitButton button {
        background-color: #E63946 !important;
        color: #FFFFFF !important;
        border: 1px solid #E63946 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    [data-testid="stMain"] .stButton button:hover,
    [data-testid="stMain"] .stFormSubmitButton button:hover {
        background-color: #C62836 !important;
        border-color: #C62836 !important;
        color: #FFFFFF !important;
    }

    /* Form containers and cards */
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #D8E1EF !important;
    }

    /* Alerts */
    [data-testid="stAlert"] * {
        color: #172033 !important;
        opacity: 1 !important;
    }

    /* Layout spacing */
    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Captions */
    [data-testid="stMain"] [data-testid="stCaptionContainer"] {
        color: #526078 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ================================ DATA HELPERS ===============================
def sample_data():
    """Return clearly labelled demonstration records for first-time startup."""
    return pd.DataFrame(
        [
            [1, "2026-01-05", "Rajampet Main Road", "High", "Clear", 2, 3, 0, 14.1950, 79.1600],
            [2, "2026-01-12", "Kadapa Bypass", "Medium", "Rain", 2, 2, 0, 14.4673, 78.8242],
            [3, "2026-02-03", "Tirupati Highway", "High", "Fog", 3, 4, 1, 13.6288, 79.4192],
            [4, "2026-02-17", "Rajampet Railway Gate", "Low", "Clear", 1, 1, 0, 14.1800, 79.1650],
            [5, "2026-03-08", "Kadapa Road Junction", "Medium", "Rain", 2, 2, 0, 14.4400, 78.8500],
            [6, "2026-03-22", "NH 716 near Nandalur", "High", "Night", 2, 3, 1, 14.2700, 79.1200],
            [7, "2026-04-01", "Rajampet Bus Stand", "Low", "Clear", 1, 0, 0, 14.1955, 79.1590],
            [8, "2026-04-16", "Kadapa City Centre", "Medium", "Cloudy", 2, 2, 0, 14.4753, 78.8350],
            [9, "2026-05-04", "NH 40 junction", "High", "Clear", 3, 5, 1, 14.3000, 78.9000],
            [10, "2026-05-19", "Rajampet Market Road", "Low", "Clear", 1, 1, 0, 14.1900, 79.1700],
            [11, "2026-06-02", "Kadapa Bypass", "High", "Rain", 2, 4, 1, 14.4600, 78.8200],
            [12, "2026-06-15", "Tirupati Highway", "Medium", "Cloudy", 2, 2, 0, 13.6400, 79.4100],
        ],
        columns=COLUMNS,
    )


def normalize_data(data):
    """Standardise imported and edited records and convert numeric/date fields."""
    data = data.copy()
    for column in COLUMNS:
        if column not in data.columns:
            data[column] = None
    data = data[COLUMNS]

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for column in ["vehicles_involved", "injuries", "fatalities", "latitude", "longitude"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    for column in ["accident_id", "location", "severity", "weather"]:
        data[column] = data[column].fillna("").astype(str).str.strip()

    data["severity"] = data["severity"].replace("", "Unknown")
    data["weather"] = data["weather"].replace("", "Unknown")
    data["location"] = data["location"].replace("", "Unknown location")
    data["accident_id"] = data["accident_id"].str.replace(r"\.0$", "", regex=True)
    return data


def save_data(data):
    """Save records to the project's local CSV file."""
    output = normalize_data(data)
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    output.to_csv(CSV_PATH, index=False)


def load_data():
    """Load the saved CSV; create demo data only on the first run."""
    if CSV_PATH.exists():
        try:
            return normalize_data(pd.read_csv(CSV_PATH))
        except Exception as exc:
            st.error(f"Could not read {CSV_PATH.name}: {exc}")
            return normalize_data(sample_data())

    data = normalize_data(sample_data())
    save_data(data)
    return data


def password_digest(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_login(username, password):
    """Check secrets.toml first, then local environment/default demo credentials."""
    try:
        expected_username = str(st.secrets["auth"]["username"])
        expected_password = str(st.secrets["auth"]["password"])
    except Exception:
        expected_username = DEFAULT_USERNAME
        expected_password = DEFAULT_PASSWORD

    return (
        hmac.compare_digest(username, expected_username)
        and hmac.compare_digest(password_digest(password), password_digest(expected_password))
    )


def valid_coordinates(data):
    """Return records with real-looking latitude/longitude values."""
    points = data.dropna(subset=["latitude", "longitude"]).copy()
    points = points[
        points["latitude"].between(-90, 90)
        & points["longitude"].between(-180, 180)
        & ~((points["latitude"] == 0) & (points["longitude"] == 0))
    ]
    return points


def style_plot(fig, height=380):
    """Apply consistent chart layout and high-contrast labels."""
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=65, b=55),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#172033", size=12),
        title_font=dict(color="#14213D", size=17),
        legend=dict(font=dict(color="#172033")),
        hoverlabel=dict(bgcolor="#101827", font_color="#FFFFFF"),
    )
    fig.update_xaxes(
        title_font=dict(color="#26354D"),
        tickfont=dict(color="#344054"),
        gridcolor="#E7ECF4",
        linecolor="#C8D2E0",
        automargin=True,
    )
    fig.update_yaxes(
        title_font=dict(color="#26354D"),
        tickfont=dict(color="#344054"),
        gridcolor="#E7ECF4",
        linecolor="#C8D2E0",
        automargin=True,
    )
    return fig


# ================================= LOGIN PAGE ================================
def login_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.05, 1])
    with center:
        st.markdown(
            """
            <div style="text-align:center; padding:10px 0 14px 0;">
                <div style="font-size:3rem;">🚦</div>
                <h1 style="margin:0; color:#14213D;">AccidentLens</h1>
                <p style="color:#526078;">Road safety analytics dashboard</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.subheader("Sign in")
            st.caption("Enter your project login details to continue.")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="admin")
                password = st.text_input("Password", type="password", placeholder="admin")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

            if submitted:
                if check_login(username.strip(), password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username.strip()
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")

        st.caption("Local demo login: admin / admin")
        st.caption("Change the demo credentials before publishing the project.")


if not st.session_state.get("authenticated", False):
    login_screen()
    st.stop()


# ================================== SIDEBAR ==================================
with st.sidebar:
    st.title("🚦 AccidentLens")
    st.caption("Road safety analytics")
    st.divider()
    page = st.radio(
        "Navigation",
        ["Dashboard", "Accident records", "Add accident", "Import / export", "Settings"],
    )
    st.divider()
    st.write(f"Signed in as **{st.session_state.get('username', 'user')}**")
    if st.button("Log out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("username", None)
        st.rerun()


# ================================= LOAD DATA =================================
df = load_data()
df["date"] = pd.to_datetime(df["date"], errors="coerce")

st.title("🚦 Road Accident Analysis")
st.markdown(
    '<p class="hero-note">Explore accident patterns, severity, locations, and trends.</p>',
    unsafe_allow_html=True,
)
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))


# ================================= DASHBOARD =================================
if page == "Dashboard":
    with st.container(border=True):
        st.subheader("Filter records")
        f1, f2, f3 = st.columns(3)

        locations = sorted(df["location"].dropna().astype(str).unique().tolist())
        severities = sorted(df["severity"].dropna().astype(str).unique().tolist())
        weather_options = sorted(df["weather"].dropna().astype(str).unique().tolist())

        with f1:
            selected_locations = st.multiselect("Location", locations, default=locations)
        with f2:
            selected_severities = st.multiselect("Severity", severities, default=severities)
        with f3:
            selected_weather = st.multiselect("Weather", weather_options, default=weather_options)

    filtered = df[
        df["location"].isin(selected_locations)
        & df["severity"].isin(selected_severities)
        & df["weather"].isin(selected_weather)
    ].copy()

    total_accidents = len(filtered)
    injury_total = int(filtered["injuries"].fillna(0).sum())
    fatality_total = int(filtered["fatalities"].fillna(0).sum())
    high_total = int(filtered["severity"].str.lower().eq("high").sum())

    st.subheader("Key statistics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total accidents", f"{total_accidents:,}")
    m2.metric("Reported injuries", f"{injury_total:,}")
    m3.metric("Fatalities", f"{fatality_total:,}")
    m4.metric("High severity", f"{high_total:,}")

    st.subheader("Accident trends")
    chart_left, chart_right = st.columns(2)

    with chart_left:
        trend_data = filtered.dropna(subset=["date"]).copy()
        if not trend_data.empty:
            trend_data["Month"] = trend_data["date"].dt.to_period("M").astype(str)
            trend = (
                trend_data.groupby("Month", as_index=False)
                .size()
                .rename(columns={"size": "Accidents"})
            )
            fig = px.line(
                trend, x="Month", y="Accidents",
                markers=True, title="Accidents by month",
                color_discrete_sequence=["#EF4444"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(style_plot(fig), use_container_width=True)
        else:
            st.info("No dated records match the selected filters.")

    with chart_right:
        if not filtered.empty:
            severity_counts = (
                filtered.groupby("severity", as_index=False)
                .size()
                .rename(columns={"size": "Accidents"})
            )
            severity_colors = {
                "Low": "#22C55E", "Medium": "#F59E0B",
                "High": "#EF4444", "Critical": "#991B1B", "Unknown": "#94A3B8",
            }
            fig = px.pie(
                severity_counts, names="severity", values="Accidents",
                hole=0.55, title="Severity distribution",
                color="severity", color_discrete_map=severity_colors,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(style_plot(fig), use_container_width=True)
        else:
            st.info("No records match the selected filters.")

    chart_left2, chart_right2 = st.columns(2)
    location_counts = (
        filtered.groupby("location", as_index=False)
        .size()
        .rename(columns={"size": "Accidents"})
        .sort_values("Accidents", ascending=False)
    )

    with chart_left2:
        if not location_counts.empty:
            fig = px.bar(
                location_counts, x="location", y="Accidents",
                title="Accidents by location",
                color="Accidents",
                color_continuous_scale=["#FCA5A5", "#EF4444", "#991B1B"],
                text="Accidents",
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_plot(fig, 420), use_container_width=True)
            st.markdown(
                f"**Highest-accident location:** {location_counts.iloc[0]['location']} "
                f"({int(location_counts.iloc[0]['Accidents'])})"
            )
            st.markdown(
                f"**Lowest-accident location:** {location_counts.iloc[-1]['location']} "
                f"({int(location_counts.iloc[-1]['Accidents'])})"
            )
        else:
            st.info("No location data is available for these filters.")

    with chart_right2:
        if not filtered.empty:
            weather_counts = (
                filtered.groupby("weather", as_index=False)
                .size()
                .rename(columns={"size": "Accidents"})
                .sort_values("Accidents", ascending=False)
            )
            fig = px.bar(
                weather_counts, x="weather", y="Accidents",
                title="Accidents by weather",
                color="weather",
                color_discrete_sequence=["#2563EB", "#06B6D4", "#F59E0B", "#8B5CF6", "#EF4444"],
                text="Accidents",
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(style_plot(fig, 420), use_container_width=True)
        else:
            st.info("No weather data is available for these filters.")

    st.subheader("Accident location map")
    map_data = valid_coordinates(filtered)
    if not map_data.empty:
        st.map(
            map_data.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]],
            use_container_width=True,
        )
        st.caption("Map markers use the latitude and longitude stored with each record.")
    else:
        st.info("No valid coordinates found. Add latitude and longitude to a record to show it on the map.")

    with st.expander("Preview filtered data"):
        preview = filtered.copy()
        preview["date"] = preview["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(preview, use_container_width=True, hide_index=True)


# ============================== ACCIDENT RECORDS =============================
elif page == "Accident records":
    st.subheader("All accident records")
    st.caption("Edit the table and select Save changes to store your edits.")

    # Keep dates as date objects for Streamlit's DateColumn.
    editable = df.copy()
    editable["date"] = pd.to_datetime(
        editable["date"], errors="coerce"
    ).dt.date

    edited = st.data_editor(
        editable,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "accident_id": st.column_config.TextColumn(
                "Accident ID",
                required=True,
            ),
            "date": st.column_config.DateColumn(
                "Date",
                format="YYYY-MM-DD",
            ),
            "location": st.column_config.TextColumn(
                "Location",
                required=True,
            ),
            "severity": st.column_config.SelectboxColumn(
                "Severity",
                options=SEVERITY_OPTIONS,
            ),
            "weather": st.column_config.SelectboxColumn(
                "Weather",
                options=WEATHER_OPTIONS,
            ),
            "vehicles_involved": st.column_config.NumberColumn(
                "Vehicles",
                min_value=0,
                step=1,
            ),
            "injuries": st.column_config.NumberColumn(
                "Injuries",
                min_value=0,
                step=1,
            ),
            "fatalities": st.column_config.NumberColumn(
                "Fatalities",
                min_value=0,
                step=1,
            ),
            "latitude": st.column_config.NumberColumn(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
            ),
            "longitude": st.column_config.NumberColumn(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                format="%.6f",
            ),
        },
        key="accident_editor",
    )

    if st.button("Save changes", type="primary"):
        cleaned = normalize_data(edited)

        ids = cleaned["accident_id"].astype(str).str.strip()

        if (ids == "").any():
            st.error("Every record must have an Accident ID.")

        elif ids.duplicated().any():
            st.error(
                "Accident IDs must be unique. "
                "Please correct duplicate IDs."
            )

        else:
            save_data(cleaned)
            st.session_state["notice"] = (
                "Accident records saved successfully."
            )
            st.rerun()

    if st.button("Delete all records"):
        st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete", False):
        st.warning(
            "This will permanently clear the local CSV data. "
            "Export a backup first."
        )

        yes_col, no_col = st.columns(2)

        if yes_col.button("Confirm delete all"):
            save_data(pd.DataFrame(columns=COLUMNS))
            st.session_state.pop("confirm_delete", None)
            st.session_state["notice"] = "All records deleted."
            st.rerun()

        if no_col.button("Cancel"):
            st.session_state.pop("confirm_delete", None)
            st.rerun()


# ================================= ADD ACCIDENT ===============================
elif page == "Add accident":
    st.subheader("Add a new accident")
    st.caption("Enter the details below. Coordinates are optional but required for map markers.")
    with st.form("add_accident_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            numeric_ids = pd.to_numeric(df["accident_id"], errors="coerce")
            next_id = int(numeric_ids.max()) + 1 if numeric_ids.notna().any() else 1
            accident_id = st.text_input("Accident ID (unique)", value=str(next_id))
            date = st.date_input("Date")
            location = st.text_input("Location", placeholder="e.g. NH 716, Rajampet")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            weather = st.selectbox("Weather", ["Clear", "Rain", "Fog", "Cloudy", "Night", "Other"])
        with right:
            vehicles = st.number_input("Vehicles involved", min_value=0, max_value=100, value=2, step=1)
            injuries_count = st.number_input("Injuries", min_value=0, max_value=1000, value=0, step=1)
            fatalities_count = st.number_input("Fatalities", min_value=0, max_value=1000, value=0, step=1)
            latitude = st.number_input("Latitude (optional; 0 means unknown)", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
            longitude = st.number_input("Longitude (optional; 0 means unknown)", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")

        submitted = st.form_submit_button("Add accident", type="primary")

    if submitted:
        if not accident_id.strip():
            st.error("Please enter an Accident ID.")
        elif not location.strip():
            st.error("Please enter a location.")
        elif accident_id.strip() in set(df["accident_id"].astype(str)):
            st.error("That Accident ID already exists. Please use a unique ID.")
        elif fatalities_count > injuries_count and injuries_count > 0:
            st.warning("Please check the injury and fatality counts before saving.")
        else:
            new_record = pd.DataFrame([{
                "accident_id": accident_id.strip(),
                "date": str(date),
                "location": location.strip(),
                "severity": severity,
                "weather": weather,
                "vehicles_involved": int(vehicles),
                "injuries": int(injuries_count),
                "fatalities": int(fatalities_count),
                "latitude": None if latitude == 0 else latitude,
                "longitude": None if longitude == 0 else longitude,
            }])
            save_data(pd.concat([df, normalize_data(new_record)], ignore_index=True))
            st.session_state["notice"] = "New accident added successfully."
            st.rerun()


# ================================ IMPORT/EXPORT ==============================
elif page == "Import / export":
    st.subheader("Import and export accident data")
    st.write("CSV columns: " + ", ".join(COLUMNS))
    export_df = df.copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        "Download current CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="accidents.csv",
        mime="text/csv",
    )

    uploaded_file = st.file_uploader("Import accident records from a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            incoming_raw = pd.read_csv(uploaded_file)
            incoming = normalize_data(incoming_raw)
            st.write("Preview imported data")
            preview = incoming.copy()
            preview["date"] = preview["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(preview, use_container_width=True, hide_index=True)
            import_mode = st.radio(
                "Import mode",
                ["Replace current records", "Append to current records"],
            )

            if st.button("Import CSV", type="primary"):
                result = (
                    incoming
                    if import_mode == "Replace current records"
                    else pd.concat([df, incoming], ignore_index=True)
                )
                result = normalize_data(result)
                ids = result["accident_id"].astype(str).str.strip()
                if (ids == "").any():
                    st.error("Import stopped: every record must have an Accident ID.")
                elif ids.duplicated().any():
                    st.error("Import stopped: duplicate Accident IDs were found.")
                else:
                    save_data(result)
                    st.session_state["notice"] = f"Imported {len(incoming)} record(s) successfully."
                    st.rerun()
        except Exception as exc:
            st.error(f"Could not import this CSV: {exc}")


# ================================== SETTINGS =================================
elif page == "Settings":
    st.subheader("Settings and setup")
    st.markdown("### Login configuration")
    st.write("Default local demo username: `admin`")
    st.write("Default local demo password: `admin`")
    st.warning(
        "These credentials are for classroom/local demonstration only. "
        "Do not publish a public app with default credentials."
    )

    st.markdown("### Change local login")
    st.write(
        "In PowerShell, set APP_USERNAME and APP_PASSWORD before starting Streamlit. "
        "For example, set them for the current terminal session:"
    )
    st.code(
        '$env:APP_USERNAME = "your_username"\n'
        '$env:APP_PASSWORD = "your_strong_password"\n'
        'python -m streamlit run app.py',
        language="powershell",
    )
    st.caption("If you set credentials in the terminal, restart the app from that same terminal.")

    st.markdown("### Data storage")
    st.write(f"Local CSV file: `{CSV_PATH.relative_to(ROOT)}`")
    st.write(
        "This project stores data on the computer running Streamlit. "
        "For a public multi-user deployment, use a hosted database and proper authentication."
    )

    st.markdown("### Dataset fields")
    st.code(", ".join(COLUMNS), language="text")

    st.markdown("### Project files")
    st.code(
        "app.py\n"
        "requirements.txt\n"
        "README.md\n"
        "data/accidents.csv\n"
        ".streamlit/secrets.toml.example",
        language="text",
    )


# ================================== FOOTER ===================================
st.divider()
st.caption(
    "AccidentLens • Educational road-safety analytics project • "
    "Sample records are for demonstration and are not official accident statistics."
)
