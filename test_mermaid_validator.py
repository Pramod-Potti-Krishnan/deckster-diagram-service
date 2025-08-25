#!/usr/bin/env python3
"""
Test Mermaid Validator
======================

Tests the MermaidValidator's ability to detect and fix Gantt chart syntax issues.
"""

import asyncio
import os
from pathlib import Path
from config.settings import Settings
from utils.mermaid_validator import MermaidValidator

# Test cases with known issues
TEST_CASES = [
    {
        "name": "Invalid status tags (des, db, int, test)",
        "input": """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    
    section Development
    System Design        :des, sysdes, after req, 9d
    Database Impl        :db, db_imp, after back, 4d
    Integration          :int, integration, after front db_imp, 3d
    Unit Testing         :test, unit_test, after integration, 3d""",
        "expected_issues": ["Invalid status tag", "des", "db", "int", "test"]
    },
    
    {
        "name": "Milestone with non-zero duration",
        "input": """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    
    section Deployment
    Testing              :test1, 2024-01-01, 7d
    Go Live              :milestone, launch, after test1, 1d
    Support              :support1, after launch, 14d""",
        "expected_issues": ["Milestone", "0d"]
    },
    
    {
        "name": "Multiple dependencies with comma (might be wrong)",
        "input": """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    
    section Development
    Frontend             :front, 2024-01-01, 10d
    Backend              :back, 2024-01-01, 10d
    Integration          :int1, after front, back, 5d""",
        "expected_issues": ["multiple dependency"]
    },
    
    {
        "name": "Valid Gantt (should pass through)",
        "input": """gantt
    title Valid Project Timeline
    dateFormat YYYY-MM-DD
    
    section Planning
    Requirements         :done, req, 2024-01-01, 7d
    Design              :active, design, after req, 10d
    Review              :milestone, review, after design, 0d
    
    section Development
    Backend             :crit, backend, after review, 14d
    Frontend            :crit, frontend, after review, 14d
    Integration         :integration, after backend frontend, 7d""",
        "expected_issues": []
    }
]


async def test_validator():
    """Test the Mermaid validator with various Gantt charts"""
    
    print("=" * 80)
    print("MERMAID VALIDATOR TEST")
    print("=" * 80)
    
    # Initialize validator
    settings = Settings()
    validator = MermaidValidator(settings)
    
    if not validator.model:
        print("⚠️  WARNING: Gemini not available - testing basic validation only")
    else:
        print("✅ Validator initialized with Gemini-2.5-Flash")
    
    print()
    
    # Test each case
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[Test {i}] {test_case['name']}")
        print("-" * 60)
        
        # Run validation
        is_valid, fixed_code, issues = await validator.validate_and_fix(
            "gantt", 
            test_case["input"]
        )
        
        # Display results
        print(f"Valid: {is_valid}")
        print(f"Issues found: {len(issues)}")
        
        if issues:
            print("Issues detected:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Check if expected issues were found
        expected = test_case["expected_issues"]
        if expected:
            found_expected = any(
                any(exp.lower() in issue.lower() for exp in expected)
                for issue in issues
            )
            if found_expected:
                print("✅ Expected issues detected")
            else:
                print("⚠️  Expected issues not fully detected")
        else:
            if issues:
                print("⚠️  Unexpected issues found (should be valid)")
            else:
                print("✅ Correctly identified as valid")
        
        # Show the fix if changes were made
        if fixed_code != test_case["input"]:
            print("\nFixed code preview (first 5 lines):")
            lines = fixed_code.split('\n')[:5]
            for line in lines:
                print(f"  {line}")
            if len(fixed_code.split('\n')) > 5:
                print(f"  ... ({len(fixed_code.split('\n')) - 5} more lines)")


async def test_specific_fix():
    """Test a specific problematic Gantt chart that was failing"""
    
    print("\n" + "=" * 80)
    print("SPECIFIC FIX TEST - Railway Generated Code")
    print("=" * 80)
    
    # This is the actual problematic code from Railway
    problematic_code = """gantt
    %% Simple project timeline based on user request and example structure
    %% Using an arbitrary "today" date of 2024-03-18 for calculations
    
    title Simple Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    excludes weekends 2024-12-25 2024-01-01 %% Example specific dates, kept for structure
    
    section Planning Phase (Week 1)
    Project Kickoff           :done, kickoff, 2024-03-18, 1d
    Requirements Gathering    :active, req, after kickoff, 4d %% Ends 2024-03-22 (Friday of Week 1)
    
    section Design Phase (Week 2-3)
    System Design             :des, sysdes, after req, 9d %% Starts 2024-03-25, ends 2024-04-04 (Thursday of Week 3)
    Design Review             :milestone, des_rev, after sysdes, 0d %% Milestone on 2024-04-05 (Friday of Week 3)
    
    section Development Phase (Week 4-6)
    Backend Development       :crit, back, after des_rev, 10d %% Starts 2024-04-08, ends 2024-04-19 (Friday of Week 5)
    Frontend Development      :crit, front, after des_rev, 12d %% Starts 2024-04-08, ends 2024-04-23 (Tuesday of Week 6)
    Database Implementation   :db, db_imp, after back, 4d %% Starts 2024-04-22, ends 2024-04-25 (Thursday of Week 6)
    Integration              :int, after front db_imp, 3d %% After both frontend and db_imp complete
    
    section Testing Phase (Week 7)
    Unit Testing             :test, unit_test, after int, 3d %% Starts after integration
    Integration Testing      :test, int_test, after unit_test, 2d
    UAT                      :uat, after int_test, 2d
    
    section Deployment (Week 8)
    Staging Deployment       :stage, after uat, 2d
    Production Release       :milestone, prod, after stage, 1d"""
    
    print("Testing problematic Railway-generated Gantt code...")
    print()
    
    settings = Settings()
    validator = MermaidValidator(settings)
    
    is_valid, fixed_code, issues = await validator.validate_and_fix(
        "gantt", 
        problematic_code
    )
    
    print(f"Valid: {is_valid}")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\nIssues detected and fixed:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Save the fixed code to a file for testing
    output_file = Path("test_fixed_gantt.md")
    with open(output_file, "w") as f:
        f.write("# Fixed Gantt Chart\n\n")
        f.write("```mermaid\n")
        f.write(fixed_code)
        f.write("\n```\n")
    
    print(f"\n📁 Fixed code saved to: {output_file}")
    print("\nYou can test this in a Mermaid viewer to verify it renders correctly.")


async def main():
    """Run all tests"""
    
    # Run validator tests
    await test_validator()
    
    # Test specific problematic code
    await test_specific_fix()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())