"""
Comprehensive Test Runner for Birthday Cake Planner
Executes all tests and generates detailed reports grouped by subject and status
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import pytest
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    """Test result data structure"""
    test_id: str
    test_name: str
    test_class: str
    test_module: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: str = ""
    error_traceback: str = ""
    markers: List[str] = None
    subject_area: str = ""
    priority: str = ""
    
    def __post_init__(self):
        if self.markers is None:
            self.markers = []


class TestReportGenerator:
    """Generates comprehensive test reports"""
    
    def __init__(self, output_dir: str = "tests/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
    
    def start_execution(self):
        """Mark start of test execution"""
        self.start_time = datetime.now()
    
    def end_execution(self):
        """Mark end of test execution"""
        self.end_time = datetime.now()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "passed"])
        failed = len([r for r in self.results if r.status == "failed"])
        skipped = len([r for r in self.results if r.status == "skipped"])
        errors = len([r for r in self.results if r.status == "error"])
        
        total_duration = sum(r.duration for r in self.results)
        execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        
        return {
            "execution_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "execution_time_seconds": execution_time,
                "total_test_time_seconds": total_duration
            },
            "test_counts": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0
            },
            "performance_metrics": {
                "average_test_duration": total_duration / total_tests if total_tests > 0 else 0,
                "slowest_tests": sorted(self.results, key=lambda x: x.duration, reverse=True)[:10],
                "fastest_tests": sorted(self.results, key=lambda x: x.duration)[:10]
            }
        }
    
    def generate_subject_report(self) -> Dict[str, Any]:
        """Generate report grouped by subject area"""
        subjects = {}
        
        for result in self.results:
            subject = result.subject_area or "uncategorized"
            if subject not in subjects:
                subjects[subject] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "errors": 0,
                    "tests": [],
                    "duration": 0
                }
            
            subjects[subject]["total"] += 1
            subjects[subject][result.status] += 1
            subjects[subject]["tests"].append(asdict(result))
            subjects[subject]["duration"] += result.duration
        
        # Calculate success rates
        for subject_data in subjects.values():
            total = subject_data["total"]
            subject_data["success_rate"] = (subject_data["passed"] / total * 100) if total > 0 else 0
        
        return subjects
    
    def generate_priority_report(self) -> Dict[str, Any]:
        """Generate report grouped by test priority"""
        priorities = {}
        
        for result in self.results:
            priority = result.priority or "medium"
            if priority not in priorities:
                priorities[priority] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "errors": 0,
                    "tests": [],
                    "duration": 0
                }
            
            priorities[priority]["total"] += 1
            priorities[priority][result.status] += 1
            priorities[priority]["tests"].append(asdict(result))
            priorities[priority]["duration"] += result.duration
        
        # Calculate success rates
        for priority_data in priorities.values():
            total = priority_data["total"]
            priority_data["success_rate"] = (priority_data["passed"] / total * 100) if total > 0 else 0
        
        return priorities
    
    def generate_failure_report(self) -> Dict[str, Any]:
        """Generate detailed failure analysis"""
        failed_tests = [r for r in self.results if r.status in ["failed", "error"]]
        
        failure_patterns = {}
        for test in failed_tests:
            error_type = test.error_message.split(":")[0] if test.error_message else "Unknown"
            if error_type not in failure_patterns:
                failure_patterns[error_type] = []
            failure_patterns[error_type].append(asdict(test))
        
        return {
            "total_failures": len(failed_tests),
            "failure_patterns": failure_patterns,
            "critical_failures": [asdict(t) for t in failed_tests if t.priority == "critical"],
            "failed_tests_by_subject": self._group_failures_by_subject(failed_tests)
        }
    
    def _group_failures_by_subject(self, failed_tests: List[TestResult]) -> Dict[str, List[Dict]]:
        """Group failed tests by subject area"""
        by_subject = {}
        for test in failed_tests:
            subject = test.subject_area or "uncategorized"
            if subject not in by_subject:
                by_subject[subject] = []
            by_subject[subject].append(asdict(test))
        return by_subject
    
    def generate_html_report(self) -> str:
        """Generate comprehensive HTML report"""
        summary = self.generate_summary_report()
        subjects = self.generate_subject_report()
        priorities = self.generate_priority_report()
        failures = self.generate_failure_report()
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Birthday Cake Planner - Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #ff6b6b, #ffa500); color: white; border-radius: 8px; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .subtitle { margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .value { font-size: 2em; font-weight: bold; color: #007bff; }
        .summary-card .label { color: #666; font-size: 0.9em; }
        .section { margin-bottom: 40px; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .status-passed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-skipped { color: #ffc107; }
        .status-error { color: #fd7e14; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; transition: width 0.3s ease; }
        .progress-passed { background: #28a745; }
        .progress-failed { background: #dc3545; }
        .progress-skipped { background: #ffc107; }
        .progress-error { background: #fd7e14; }
        .test-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .test-table th, .test-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .test-table th { background: #f8f9fa; font-weight: bold; }
        .test-table tr:hover { background: #f5f5f5; }
        .collapsible { background: #f1f1f1; color: #333; cursor: pointer; padding: 15px; width: 100%; border: none; text-align: left; outline: none; font-size: 16px; border-radius: 4px; margin: 5px 0; }
        .collapsible:hover { background: #ddd; }
        .collapsible.active { background: #007bff; color: white; }
        .content { padding: 0 15px; display: none; overflow: hidden; background: #f9f9f9; border-radius: 0 0 4px 4px; }
        .content.show { display: block; padding: 15px; }
        .error-details { background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 10px; margin: 10px 0; font-family: monospace; font-size: 0.9em; }
        .cake-emoji { font-size: 1.5em; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="cake-emoji">🎂</span> Birthday Cake Planner</h1>
            <div class="subtitle">Comprehensive Test Report</div>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{total_tests}</div>
                <div class="label">Test cases executed</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="value status-passed">{success_rate:.1f}%</div>
                <div class="label">Tests passed</div>
            </div>
            <div class="summary-card">
                <h3>Execution Time</h3>
                <div class="value">{execution_time:.1f}s</div>
                <div class="label">Total duration</div>
            </div>
            <div class="summary-card">
                <h3>Failed Tests</h3>
                <div class="value status-failed">{failed_tests}</div>
                <div class="label">Require attention</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Test Status Overview</h2>
            <div class="progress-bar">
                <div class="progress-fill progress-passed" style="width: {passed_percent}%"></div>
                <div class="progress-fill progress-failed" style="width: {failed_percent}%"></div>
                <div class="progress-fill progress-skipped" style="width: {skipped_percent}%"></div>
                <div class="progress-fill progress-error" style="width: {error_percent}%"></div>
            </div>
            <div style="margin-top: 10px;">
                <span class="status-passed">■ Passed: {passed_tests}</span> |
                <span class="status-failed">■ Failed: {failed_tests}</span> |
                <span class="status-skipped">■ Skipped: {skipped_tests}</span> |
                <span class="status-error">■ Errors: {error_tests}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Results by Subject Area</h2>
            {subject_sections}
        </div>
        
        <div class="section">
            <h2>Results by Priority</h2>
            {priority_sections}
        </div>
        
        {failure_section}
        
        <div class="section">
            <h2>Performance Analysis</h2>
            <h3>Slowest Tests</h3>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Duration (s)</th>
                        <th>Subject</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {slowest_tests}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Make collapsible sections work
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                content.classList.toggle("show");
            });
        }
    </script>
</body>
</html>
        """
        
        # Format the template with data
        return html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=summary["test_counts"]["total"],
            success_rate=summary["test_counts"]["success_rate"],
            execution_time=summary["execution_summary"]["execution_time_seconds"],
            failed_tests=summary["test_counts"]["failed"],
            passed_tests=summary["test_counts"]["passed"],
            skipped_tests=summary["test_counts"]["skipped"],
            error_tests=summary["test_counts"]["errors"],
            passed_percent=summary["test_counts"]["passed"] / summary["test_counts"]["total"] * 100 if summary["test_counts"]["total"] > 0 else 0,
            failed_percent=summary["test_counts"]["failed"] / summary["test_counts"]["total"] * 100 if summary["test_counts"]["total"] > 0 else 0,
            skipped_percent=summary["test_counts"]["skipped"] / summary["test_counts"]["total"] * 100 if summary["test_counts"]["total"] > 0 else 0,
            error_percent=summary["test_counts"]["errors"] / summary["test_counts"]["total"] * 100 if summary["test_counts"]["total"] > 0 else 0,
            subject_sections=self._generate_subject_html(subjects),
            priority_sections=self._generate_priority_html(priorities),
            failure_section=self._generate_failure_html(failures) if failures["total_failures"] > 0 else "",
            slowest_tests=self._generate_slowest_tests_html(summary["performance_metrics"]["slowest_tests"])
        )
    
    def _generate_subject_html(self, subjects: Dict[str, Any]) -> str:
        """Generate HTML for subject sections"""
        html = ""
        for subject, data in subjects.items():
            success_rate = data["success_rate"]
            status_class = "status-passed" if success_rate >= 90 else "status-failed" if success_rate < 70 else "status-skipped"
            
            html += f"""
            <button class="collapsible">{subject.title()} - {data['total']} tests ({success_rate:.1f}% success)</button>
            <div class="content">
                <div class="progress-bar">
                    <div class="progress-fill progress-passed" style="width: {data['passed']/data['total']*100 if data['total'] > 0 else 0}%"></div>
                </div>
                <p>
                    <span class="status-passed">Passed: {data['passed']}</span> |
                    <span class="status-failed">Failed: {data['failed']}</span> |
                    <span class="status-skipped">Skipped: {data['skipped']}</span> |
                    <span class="status-error">Errors: {data['errors']}</span>
                </p>
                <p>Total Duration: {data['duration']:.2f}s</p>
            </div>
            """
        return html
    
    def _generate_priority_html(self, priorities: Dict[str, Any]) -> str:
        """Generate HTML for priority sections"""
        html = ""
        priority_order = ["critical", "high", "medium", "low"]
        
        for priority in priority_order:
            if priority in priorities:
                data = priorities[priority]
                success_rate = data["success_rate"]
                
                html += f"""
                <button class="collapsible">{priority.title()} Priority - {data['total']} tests ({success_rate:.1f}% success)</button>
                <div class="content">
                    <div class="progress-bar">
                        <div class="progress-fill progress-passed" style="width: {data['passed']/data['total']*100 if data['total'] > 0 else 0}%"></div>
                    </div>
                    <p>
                        <span class="status-passed">Passed: {data['passed']}</span> |
                        <span class="status-failed">Failed: {data['failed']}</span> |
                        <span class="status-skipped">Skipped: {data['skipped']}</span> |
                        <span class="status-error">Errors: {data['errors']}</span>
                    </p>
                </div>
                """
        return html
    
    def _generate_failure_html(self, failures: Dict[str, Any]) -> str:
        """Generate HTML for failure analysis"""
        if failures["total_failures"] == 0:
            return ""
        
        html = f"""
        <div class="section">
            <h2>Failure Analysis ({failures['total_failures']} failures)</h2>
        """
        
        for error_type, tests in failures["failure_patterns"].items():
            html += f"""
            <button class="collapsible">{error_type} ({len(tests)} occurrences)</button>
            <div class="content">
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Subject</th>
                            <th>Error Message</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for test in tests:
                html += f"""
                        <tr>
                            <td>{test['test_name']}</td>
                            <td>{test['subject_area']}</td>
                            <td><div class="error-details">{test['error_message'][:200]}...</div></td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_slowest_tests_html(self, slowest_tests: List[Dict]) -> str:
        """Generate HTML for slowest tests table"""
        html = ""
        for test in slowest_tests[:10]:
            status_class = f"status-{test['status']}"
            html += f"""
                <tr>
                    <td>{test['test_name']}</td>
                    <td>{test['duration']:.2f}</td>
                    <td>{test['subject_area']}</td>
                    <td><span class="{status_class}">{test['status'].title()}</span></td>
                </tr>
            """
        return html
    
    def save_reports(self):
        """Save all reports to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON reports
        summary = self.generate_summary_report()
        subjects = self.generate_subject_report()
        priorities = self.generate_priority_report()
        failures = self.generate_failure_report()
        
        # Save JSON reports
        with open(self.output_dir / f"test_summary_{timestamp}.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        with open(self.output_dir / f"test_subjects_{timestamp}.json", "w") as f:
            json.dump(subjects, f, indent=2, default=str)
        
        with open(self.output_dir / f"test_priorities_{timestamp}.json", "w") as f:
            json.dump(priorities, f, indent=2, default=str)
        
        with open(self.output_dir / f"test_failures_{timestamp}.json", "w") as f:
            json.dump(failures, f, indent=2, default=str)
        
        # Save HTML report
        html_report = self.generate_html_report()
        with open(self.output_dir / f"test_report_{timestamp}.html", "w") as f:
            f.write(html_report)
        
        # Save latest report (overwrite)
        with open(self.output_dir / "latest_report.html", "w") as f:
            f.write(html_report)
        
        with open(self.output_dir / "latest_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        return {
            "html_report": self.output_dir / f"test_report_{timestamp}.html",
            "json_summary": self.output_dir / f"test_summary_{timestamp}.json",
            "latest_html": self.output_dir / "latest_report.html"
        }


class BirthdayCakeTestRunner:
    """Main test runner for Birthday Cake Planner"""
    
    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.report_generator = TestReportGenerator()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        config_file = self.test_dir / "config" / "test_config.py"
        if config_file.exists():
            # Import configuration
            sys.path.insert(0, str(self.test_dir))
            try:
                from config.test_config import TestConfig
                return TestConfig.__dict__
            except ImportError:
                pass
        
        # Default configuration
        return {
            "PARALLEL_WORKERS": 4,
            "TIMEOUT_SECONDS": 300,
            "RETRY_FAILED_TESTS": True,
            "GENERATE_COVERAGE": True
        }
    
    def run_all_tests(self, markers: List[str] = None, parallel: bool = True) -> Dict[str, Any]:
        """Run all tests with specified markers"""
        print("🎂 Starting Birthday Cake Planner Test Suite 🎂")
        print("=" * 60)
        
        self.report_generator.start_execution()
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test directories
        cmd.extend([
            str(self.test_dir / "backend"),
            str(self.test_dir / "frontend"),
            str(self.test_dir / "integration")
        ])
        
        # Add markers if specified
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # Add parallel execution
        if parallel and self.config.get("PARALLEL_WORKERS", 1) > 1:
            cmd.extend(["-n", str(self.config["PARALLEL_WORKERS"])])
        
        # Add coverage if enabled
        if self.config.get("GENERATE_COVERAGE", False):
            cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        
        # Add verbose output
        cmd.extend(["-v", "--tb=short"])
        
        # Add JSON report
        json_report_file = self.test_dir / "reports" / "pytest_results.json"
        cmd.extend(["--json-report", f"--json-report-file={json_report_file}"])
        
        print(f"Executing: {' '.join(cmd)}")
        print("-" * 60)
        
        # Run tests
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir.parent)
            
            # Parse results
            self._parse_pytest_results(json_report_file)
            
        except Exception as e:
            print(f"Error running tests: {e}")
            return {"success": False, "error": str(e)}
        
        self.report_generator.end_execution()
        
        # Generate reports
        report_files = self.report_generator.save_reports()
        
        # Print summary
        self._print_summary()
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "report_files": report_files
        }
    
    def _parse_pytest_results(self, json_file: Path):
        """Parse pytest JSON results"""
        if not json_file.exists():
            return
        
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            for test in data.get("tests", []):
                # Extract test information
                test_id = test.get("nodeid", "")
                test_name = test_id.split("::")[-1] if "::" in test_id else test_id
                test_class = test_id.split("::")[-2] if test_id.count("::") >= 2 else ""
                test_module = test_id.split("::")[0] if "::" in test_id else ""
                
                # Determine subject area and priority from markers or path
                markers = [marker.get("name", "") for marker in test.get("markers", [])]
                subject_area = self._extract_subject_area(test_module, markers)
                priority = self._extract_priority(markers)
                
                # Create test result
                result = TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    test_class=test_class,
                    test_module=test_module,
                    status=test.get("outcome", "unknown"),
                    duration=test.get("duration", 0),
                    error_message=test.get("call", {}).get("longrepr", ""),
                    markers=markers,
                    subject_area=subject_area,
                    priority=priority
                )
                
                self.report_generator.add_result(result)
                
        except Exception as e:
            print(f"Error parsing test results: {e}")
    
    def _extract_subject_area(self, module_path: str, markers: List[str]) -> str:
        """Extract subject area from module path or markers"""
        # Check markers first
        subject_markers = [
            "authentication", "task_management", "ai_personality", 
            "ui_functionality", "integration", "performance", "security"
        ]
        
        for marker in markers:
            if marker in subject_markers:
                return marker
        
        # Extract from module path
        if "auth" in module_path:
            return "authentication"
        elif "task" in module_path:
            return "task_management"
        elif "ai" in module_path or "cake" in module_path:
            return "ai_personality"
        elif "ui" in module_path or "frontend" in module_path:
            return "ui_functionality"
        elif "integration" in module_path or "e2e" in module_path:
            return "integration"
        elif "performance" in module_path:
            return "performance"
        elif "security" in module_path:
            return "security"
        else:
            return "general"
    
    def _extract_priority(self, markers: List[str]) -> str:
        """Extract priority from markers"""
        priority_markers = ["critical", "high", "medium", "low"]
        
        for marker in markers:
            if marker in priority_markers:
                return marker
        
        return "medium"  # Default priority
    
    def _print_summary(self):
        """Print test execution summary"""
        summary = self.report_generator.generate_summary_report()
        
        print("\n" + "=" * 60)
        print("🎂 BIRTHDAY CAKE PLANNER TEST SUMMARY 🎂")
        print("=" * 60)
        
        counts = summary["test_counts"]
        print(f"Total Tests: {counts['total']}")
        print(f"✅ Passed: {counts['passed']}")
        print(f"❌ Failed: {counts['failed']}")
        print(f"⏭️  Skipped: {counts['skipped']}")
        print(f"💥 Errors: {counts['errors']}")
        print(f"📊 Success Rate: {counts['success_rate']:.1f}%")
        
        execution = summary["execution_summary"]
        print(f"⏱️  Execution Time: {execution['execution_time_seconds']:.1f}s")
        
        print("\n📋 SUBJECT AREA BREAKDOWN:")
        subjects = self.report_generator.generate_subject_report()
        for subject, data in subjects.items():
            status_emoji = "✅" if data["success_rate"] >= 90 else "⚠️" if data["success_rate"] >= 70 else "❌"
            print(f"  {status_emoji} {subject.title()}: {data['passed']}/{data['total']} ({data['success_rate']:.1f}%)")
        
        if counts['failed'] > 0 or counts['errors'] > 0:
            print("\n🚨 CRITICAL ISSUES:")
            failures = self.report_generator.generate_failure_report()
            for error_type, tests in failures["failure_patterns"].items():
                print(f"  • {error_type}: {len(tests)} occurrences")
        
        print("\n📁 Reports generated in: tests/reports/")
        print("🌐 Open latest_report.html for detailed analysis")
        print("=" * 60)


def main():
    """Main entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Birthday Cake Planner Test Runner")
    parser.add_argument("--markers", "-m", nargs="+", help="Test markers to run")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--critical-only", action="store_true", help="Run only critical tests")
    parser.add_argument("--subject", choices=[
        "authentication", "task_management", "ai_personality", 
        "ui_functionality", "integration", "performance", "security"
    ], help="Run tests for specific subject area")
    
    args = parser.parse_args()
    
    # Build markers list
    markers = args.markers or []
    
    if args.critical_only:
        markers.append("critical")
    
    if args.subject:
        markers.append(args.subject)
    
    # Run tests
    runner = BirthdayCakeTestRunner()
    result = runner.run_all_tests(
        markers=markers if markers else None,
        parallel=not args.no_parallel
    )
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

