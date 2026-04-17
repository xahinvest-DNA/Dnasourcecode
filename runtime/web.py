from __future__ import annotations

import argparse
import html
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from runtime.engine import CycleEngine, GuardrailError
from runtime.storage import LocalJsonStore


def run_server(host: str = "127.0.0.1", port: int = 8000, data_dir: str = "data") -> None:
    engine = CycleEngine(LocalJsonStore(Path(data_dir)))
    server = ThreadingHTTPServer((host, port), _build_handler(engine))
    print(f"Running minimal restructuring loop at http://{host}:{port}")
    server.serve_forever()


def _build_handler(engine: CycleEngine):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                cycles = engine.store.list_cycle_records()
                self._respond_html(_render_home(cycles))
                return
            if parsed.path.startswith("/cycles/"):
                cycle_id = parsed.path.split("/")[2]
                try:
                    cycle = engine.store.load_cycle_record(cycle_id)
                except FileNotFoundError:
                    self._respond_html(_render_error("Cycle not found."), status=HTTPStatus.NOT_FOUND)
                    return
                self._respond_html(_render_cycle(cycle))
                return
            self._respond_html(_render_error("Not found."), status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8")
            form = {key: values[0] for key, values in parse_qs(raw_body).items()}
            try:
                if parsed.path == "/cycles":
                    cycle = engine.create_cycle(
                        problem_summary=form.get("problem_summary", ""),
                        repeated_pattern_summary=form.get("repeated_pattern_summary", ""),
                        desired_shift=form.get("desired_shift", ""),
                    )
                    self._redirect(f"/cycles/{cycle['cycle_id']}")
                    return
                if parsed.path.startswith("/cycles/") and parsed.path.endswith("/checkin"):
                    cycle_id = parsed.path.split("/")[2]
                    engine.submit_checkin(
                        cycle_id=cycle_id,
                        completion_status=form.get("completion_status", ""),
                        observed_external_result=form.get("observed_external_result", ""),
                        observed_internal_reaction=form.get("observed_internal_reaction", ""),
                        old_cycle_return_note=form.get("old_cycle_return_note", ""),
                    )
                    self._redirect(f"/cycles/{cycle_id}")
                    return
                self._respond_html(_render_error("Unsupported action."), status=HTTPStatus.NOT_FOUND)
            except GuardrailError as error:
                self._respond_html(_render_error(str(error)), status=HTTPStatus.BAD_REQUEST)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _respond_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _redirect(self, location: str) -> None:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", location)
            self.end_headers()

    return Handler


def _render_home(cycles: list[dict]) -> str:
    rows = []
    for cycle in cycles:
        rows.append(
            "<li>"
            f"<a href='/cycles/{html.escape(cycle['cycle_id'])}'>{html.escape(cycle['cycle_id'])}</a> "
            f"- state: <strong>{html.escape(cycle['process_state'])}</strong> "
            f"- resolution: <strong>{html.escape(cycle['resolution_status'])}</strong>"
            "</li>"
        )
    cycles_html = "<ul>" + "".join(rows) + "</ul>" if rows else "<p>No cycles yet.</p>"
    return _page(
        "Minimal Executable Restructuring Loop",
        f"""
        <h1>Minimal Executable Restructuring Loop</h1>
        <p>Create one money/income cycle, review generated artifacts, then return with a check-in.</p>
        <form method="post" action="/cycles">
          <label>Current money/income problem</label>
          <textarea name="problem_summary" required></textarea>
          <label>Repeated pattern</label>
          <textarea name="repeated_pattern_summary" required></textarea>
          <label>Desired shift</label>
          <textarea name="desired_shift"></textarea>
          <button type="submit">Start cycle</button>
        </form>
        <h2>Stored cycles</h2>
        {cycles_html}
        """,
    )


def _render_cycle(cycle: dict) -> str:
    sections = [
        _artifact_section("Intake Record", cycle.get("intake_record")),
        _artifact_section("DNA Support Signals", cycle.get("dna_support_signals")),
        _artifact_section("Diagnosis Output", cycle.get("diagnosis_output")),
        _artifact_section("Old Cycle Map", cycle.get("old_cycle_map")),
        _artifact_section("Restructuring Output", cycle.get("restructuring_output")),
        _artifact_section("Action Output", cycle.get("action_output")),
        _artifact_section("Check-In Output", cycle.get("checkin_output")),
        _artifact_section("Progress Snapshot", cycle.get("progress_snapshot")),
    ]
    checkin_form = ""
    if cycle["process_state"] == "action_assigned":
        checkin_form = f"""
        <section>
          <h2>Submit check-in</h2>
          <form method="post" action="/cycles/{html.escape(cycle['cycle_id'])}/checkin">
            <label>Completion status</label>
            <select name="completion_status">
              <option value="completed">completed</option>
              <option value="partial">partial</option>
              <option value="not_completed">not_completed</option>
            </select>
            <label>Observed external result</label>
            <textarea name="observed_external_result" required></textarea>
            <label>Observed internal reaction</label>
            <textarea name="observed_internal_reaction" required></textarea>
            <label>Old cycle return note</label>
            <textarea name="old_cycle_return_note" required></textarea>
            <button type="submit">Resolve cycle</button>
          </form>
        </section>
        """
    return _page(
        f"Cycle {cycle['cycle_id']}",
        f"""
        <p><a href="/">Back to home</a></p>
        <h1>{html.escape(cycle['cycle_id'])}</h1>
        <p>Process state: <strong>{html.escape(cycle['process_state'])}</strong></p>
        <p>Resolution status: <strong>{html.escape(cycle['resolution_status'])}</strong></p>
        {''.join(sections)}
        {checkin_form}
        """,
    )


def _artifact_section(title: str, artifact: dict | None) -> str:
    if not artifact:
        return f"<section><h2>{html.escape(title)}</h2><p>Not created yet.</p></section>"
    items = "".join(
        f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(_format_value(value))}</td></tr>"
        for key, value in artifact.items()
    )
    return f"<section><h2>{html.escape(title)}</h2><table>{items}</table></section>"


def _format_value(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _render_error(message: str) -> str:
    return _page("Error", f"<p><a href='/'>Back to home</a></p><h1>Error</h1><p>{html.escape(message)}</p>")


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 2rem auto;
      max-width: 920px;
      padding: 0 1rem 3rem;
      line-height: 1.45;
    }}
    form, section {{
      border: 1px solid #d5d5d5;
      padding: 1rem;
      margin: 1rem 0;
      border-radius: 6px;
      background: #fafafa;
    }}
    textarea, select {{
      width: 100%;
      min-height: 4rem;
      margin: 0.4rem 0 1rem;
      padding: 0.6rem;
      box-sizing: border-box;
    }}
    select {{
      min-height: auto;
    }}
    button {{
      padding: 0.7rem 1rem;
      border: 0;
      background: #1d4ed8;
      color: white;
      border-radius: 4px;
      cursor: pointer;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      text-align: left;
      padding: 0.5rem;
      border-top: 1px solid #e5e5e5;
      vertical-align: top;
    }}
    th {{
      width: 30%;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, data_dir=args.data_dir)


if __name__ == "__main__":
    main()
