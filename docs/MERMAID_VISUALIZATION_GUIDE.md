# Mermaid.js Visualization Guide

## Table of Contents
1. [Introduction](#introduction)
2. [General Setup](#general-setup)
3. [Common Visualization Issues](#common-visualization-issues)
4. [Gantt Chart Visualization Guide](#gantt-chart-visualization-guide)
5. [Theme Configuration Reference](#theme-configuration-reference)
6. [Best Practices](#best-practices)
7. [Complete HTML Template](#complete-html-template)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

This guide provides comprehensive solutions for visualizing Mermaid diagrams with optimal readability and aesthetics. While it focuses on Gantt charts (which present unique challenges), the principles apply to all Mermaid diagram types.

### Version Requirements
- **Mermaid v10.9.1**: Supports most diagram types except Kanban
- **Mermaid v11+**: Required for Kanban boards, recommended for all diagrams
- Always use the latest stable version when possible

```html
<!-- Recommended: Mermaid v11 -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
```

---

## General Setup

### Basic Initialization

```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    themeVariables: {
        // Custom theme variables go here
    }
});
```

### Common Issues Across All Diagram Types

1. **Text Contrast Problems**: White or light text on light backgrounds
2. **Grid/Line Visibility**: Faint lines that don't show clearly
3. **Color Accessibility**: Poor contrast ratios failing WCAG standards
4. **Version Compatibility**: Certain diagrams not rendering in older versions

---

## Common Visualization Issues

### Issue 1: Unreadable Text
**Problem**: Text appears white or too light on light-colored backgrounds
**Solution**: Set explicit text colors for different backgrounds

```javascript
themeVariables: {
    taskTextColor: '#1f2937',      // Dark text for light backgrounds
    taskTextDarkColor: '#ffffff',  // White text for dark backgrounds
    primaryTextColor: '#1f2937',   // Primary text in dark color
}
```

### Issue 2: Invisible Grid Lines
**Problem**: Grid lines too faint or not extending properly
**Solution**: Darken grid colors and ensure proper configuration

```javascript
themeVariables: {
    gridColor: '#9ca3af',  // Darker gray for visibility
    lineColor: '#6b7280',  // Ensure lines are visible
}
```

### Issue 3: Overwhelming Background Patterns
**Problem**: Weekend exclusions or backgrounds too prominent
**Solution**: Use subtle colors for non-essential elements

```javascript
themeVariables: {
    excludeBkgColor: '#fafafa',  // Very subtle gray instead of yellow
}
```

---

## Gantt Chart Visualization Guide

Gantt charts present unique challenges due to their complex structure with multiple task states, dependencies, and timeline elements.

### Critical Gantt-Specific Issues and Solutions

#### 1. Task State Text Contrast

Gantt charts have multiple task states, each requiring different text colors:

```javascript
gantt: {
    useMaxWidth: true,
    numberSectionStyles: 4,
    fontSize: 12,  // Ensure readable font size
    topAxis: true  // Extend grid lines to top
},
themeVariables: {
    // Task backgrounds
    doneTaskBkgColor: '#9ca3af',     // Gray for completed
    activeTaskBkgColor: '#3B82F6',   // Blue for active
    critBkgColor: '#ef4444',         // Red for critical
    taskBkgColor: '#f3f4f6',         // Light gray for normal
    
    // CRITICAL: Specific text colors for each state
    doneTaskTextColor: '#1f2937',    // Dark text on gray
    activeTaskTextColor: '#ffffff',   // White text on blue
    critTaskTextColor: '#ffffff',     // White text on red
    taskTextColor: '#1f2937',        // Dark text on light gray
}
```

#### 2. Weekend/Holiday Exclusions

Default yellow stripes can be visually overwhelming:

```javascript
themeVariables: {
    // Change from bright yellow to subtle gray
    excludeBkgColor: '#fafafa',  // Nearly invisible light gray
    // Or completely transparent
    // excludeBkgColor: 'transparent',
}
```

#### 3. Grid Line Display

Ensure timeline grid lines are visible and extend properly:

```javascript
gantt: {
    topAxis: true,  // Critical: Makes grid lines extend to top
    gridLineStartPadding: 350,  // Adjust based on task name length
    leftPadding: 200,  // Space for task names
},
themeVariables: {
    gridColor: '#9ca3af',  // Darker than default for visibility
    todayLineColor: '#ef4444',  // Make "today" marker visible
}
```

#### 4. Section Headers

Ensure section labels are readable:

```javascript
gantt: {
    sectionFontSize: 14,  // Larger section headers
    fontFamily: '"Trebuchet MS", verdana, arial, sans-serif',
},
themeVariables: {
    sectionBkgColor: '#ffffff',
    sectionBkgColor2: '#f9fafb',  // Alternating section colors
}
```

### Complete Gantt Configuration

```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    gantt: {
        useMaxWidth: true,
        numberSectionStyles: 4,
        fontSize: 12,
        gridLineStartPadding: 350,
        leftPadding: 200,
        sectionFontSize: 14,
        topAxis: true,  // Critical for grid lines
        fontFamily: '"Trebuchet MS", verdana, arial, sans-serif'
    },
    themeVariables: {
        // Task backgrounds
        critBkgColor: '#ef4444',
        critBorderColor: '#dc2626',
        doneTaskBkgColor: '#9ca3af',
        doneTaskBorderColor: '#6b7280',
        activeTaskBkgColor: '#3B82F6',
        activeTaskBorderColor: '#2563EB',
        taskBkgColor: '#f3f4f6',
        taskBorderColor: '#9ca3af',
        
        // Text colors - Critical for readability
        taskTextColor: '#1f2937',
        taskTextDarkColor: '#ffffff',
        taskTextOutsideColor: '#1f2937',
        doneTaskTextColor: '#1f2937',
        activeTaskTextColor: '#ffffff',
        critTaskTextColor: '#ffffff',
        
        // Grid and timeline
        gridColor: '#9ca3af',
        todayLineColor: '#ef4444',
        excludeBkgColor: '#fafafa',
        
        // General text
        primaryTextColor: '#1f2937',
        labelColor: '#1f2937',
        titleColor: '#1f2937'
    }
});
```

---

## Theme Configuration Reference

### Universal Theme Variables

These variables work across all diagram types:

| Variable | Purpose | Recommended Value |
|----------|---------|-------------------|
| `primaryColor` | Main theme color | `#3B82F6` |
| `primaryTextColor` | Primary text color | `#1f2937` (dark) |
| `primaryBorderColor` | Border color | `#2563EB` |
| `lineColor` | General line color | `#6b7280` |
| `textColor` | General text | `#1f2937` |
| `mainBkg` | Main background | `#ffffff` |
| `gridColor` | Grid lines | `#9ca3af` |

### Gantt-Specific Variables

| Variable | Purpose | Light Theme | Dark Theme |
|----------|---------|-------------|------------|
| `taskTextColor` | Normal task text | `#1f2937` | `#e5e7eb` |
| `doneTaskTextColor` | Completed task text | `#1f2937` | `#e5e7eb` |
| `activeTaskTextColor` | Active task text | `#ffffff` | `#ffffff` |
| `critTaskTextColor` | Critical task text | `#ffffff` | `#ffffff` |
| `excludeBkgColor` | Weekend/holiday bg | `#fafafa` | `#1f2937` |

---

## Best Practices

### 1. Color Contrast Guidelines

Follow WCAG AA standards for text contrast:
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text**: Minimum 3:1 contrast ratio
- **Active elements**: Minimum 3:1 contrast ratio

### 2. Testing Your Configuration

Always test with different content scenarios:

```javascript
// Test data covering all states
const testGantt = `
gantt
    title Test All States
    section Test
    Completed Task     :done, task1, 2024-01-01, 3d
    Active Task        :active, task2, after task1, 3d
    Critical Task      :crit, task3, after task2, 3d
    Normal Task        :task4, after task3, 3d
    Milestone         :milestone, m1, after task4, 0d
`;
```

### 3. Responsive Design

Ensure diagrams work on different screen sizes:

```css
.mermaid-wrapper {
    overflow-x: auto;  /* Allow horizontal scroll on small screens */
    max-width: 100%;
}

.mermaid {
    min-width: 600px;  /* Minimum width for readability */
}
```

### 4. Version-Specific Features

Check version compatibility:

```javascript
// Detect Mermaid version
if (typeof mermaid !== 'undefined' && mermaid.version) {
    const version = mermaid.version;
    console.log(`Mermaid version: ${version}`);
    
    // Conditionally enable features
    if (version.startsWith('11')) {
        // Enable v11-specific features like Kanban
    }
}
```

---

## Complete HTML Template

Here's a production-ready template with all optimizations:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Optimized Mermaid Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }
        
        .mermaid-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        
        .mermaid {
            min-width: 600px;
        }
        
        /* Gantt-specific styling */
        .gantt-container .mermaid {
            min-width: 1000px;
        }
    </style>
</head>
<body>
    <div class="mermaid-container">
        <div class="mermaid">
            <!-- Your Mermaid code here -->
        </div>
    </div>
    
    <script>
        // Optimized Mermaid configuration
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            gantt: {
                useMaxWidth: true,
                numberSectionStyles: 4,
                fontSize: 12,
                topAxis: true,
                gridLineStartPadding: 350,
                leftPadding: 200,
                sectionFontSize: 14
            },
            themeVariables: {
                // Backgrounds
                taskBkgColor: '#f3f4f6',
                doneTaskBkgColor: '#9ca3af',
                activeTaskBkgColor: '#3B82F6',
                critBkgColor: '#ef4444',
                
                // Text colors (critical for readability)
                taskTextColor: '#1f2937',
                doneTaskTextColor: '#1f2937',
                activeTaskTextColor: '#ffffff',
                critTaskTextColor: '#ffffff',
                taskTextOutsideColor: '#1f2937',
                
                // Grid and timeline
                gridColor: '#9ca3af',
                excludeBkgColor: '#fafafa',
                
                // General
                primaryTextColor: '#1f2937',
                primaryColor: '#3B82F6'
            }
        });
    </script>
</body>
</html>
```

---

## Troubleshooting

### Quick Fixes for Common Issues

| Problem | Quick Fix |
|---------|-----------|
| White text on gray background | Add `doneTaskTextColor: '#1f2937'` |
| Yellow weekend stripes | Change `excludeBkgColor: '#fafafa'` |
| Grid lines not showing at top | Add `topAxis: true` to gantt config |
| Text too small | Increase `fontSize` in gantt config |
| Task names cut off | Increase `leftPadding` and `gridLineStartPadding` |
| Can't see grid lines | Darken `gridColor: '#9ca3af'` |
| Milestones not visible | Set `milestoneBackgroundColor: '#fbbf24'` |

### Debug Mode

Enable debug information:

```javascript
mermaid.initialize({
    startOnLoad: true,
    logLevel: 'debug',  // Shows detailed logs
    // ... rest of config
});

// Check rendered diagram
mermaid.init(undefined, document.querySelectorAll('.mermaid'));
```

### Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: May need webkit prefixes for some CSS
- **IE11**: Not supported (use Chrome/Edge)

---

## Conclusion

Proper Mermaid visualization requires careful attention to:
1. **Text contrast** - Ensure readability on all backgrounds
2. **Grid visibility** - Make structural elements clear
3. **Color accessibility** - Follow WCAG guidelines
4. **Version compatibility** - Use appropriate version for features needed

For Gantt charts specifically, pay special attention to task state colors and weekend exclusion zones, as these are the most common sources of readability issues.

Remember: The goal is to make diagrams that are not just functional, but also accessible and visually pleasant for all users.