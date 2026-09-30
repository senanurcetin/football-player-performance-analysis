const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const projectRoot = path.resolve(__dirname, "..");
const reportRoot = path.join(
  projectRoot,
  "powerbi",
  "workspace",
  "FootballPlayerAnalysis",
  "Report",
  "sections",
);

const palette = {
  page: "#CFF8C9",
  panel: "#F6FBF5",
  panelAlt: "#EAF6E8",
  border: "#8BC99A",
  accent: "#119A91",
  accentDark: "#0F4B3B",
  accentMuted: "#2E6B45",
  text: "#20323F",
  muted: "#536A60",
  header: "#285D3D",
  white: "#FFFFFF",
};

// ─── Page helpers ────────────────────────────────────────────────────────────

function findPage(prefix) {
  const name = fs.readdirSync(reportRoot).find((entry) => entry.startsWith(prefix));
  if (!name) throw new Error(`Could not find page with prefix ${prefix}`);
  return path.join(reportRoot, name);
}

function ensurePage(prefix, folderName, displayName, ordinal) {
  const existing = fs.readdirSync(reportRoot).find((entry) => entry.startsWith(prefix));
  const pagePath = path.join(reportRoot, existing || folderName);
  fs.mkdirSync(path.join(pagePath, "visualContainers"), { recursive: true });
  writeJson(path.join(pagePath, "section.json"), {
    displayName,
    displayOption: 1,
    height: 720,
    name: folderName.replace(/^[0-9]+_/, "").replace(/[^A-Za-z0-9]/g, ""),
    ordinal,
    width: 1280,
  });
  writeJson(path.join(pagePath, "config.json"), pageConfig(true));
  writeJson(path.join(pagePath, "filters.json"), []);
  return pagePath;
}

const pages = {
  transfer: findPage("005_"),
  ml: findPage("006_"),
  transferDetail: ensurePage("008_", "008_Transfer Player Detail", "Transfer Oyuncu Detayi", 8),
  mlDetail: ensurePage("009_", "009_ML Player Detail", "Oyuncu Tahmin Detayi", 9),
  mlPerformance: ensurePage("010_", "010_ML Model Performance", "ML Model Guvenilirligi", 10),
};

// ─── JSON primitives ─────────────────────────────────────────────────────────

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2));
}

function literal(value) {
  return { expr: { Literal: { Value: value } } };
}

function color(value) {
  return { solid: { color: literal(`'${value}'`) } };
}

// ─── Page config ─────────────────────────────────────────────────────────────

function pageConfig(isDrillthrough = false) {
  const config = {
    objects: {
      background: [
        { properties: { color: color(palette.page), transparency: literal("0D") } },
      ],
    },
  };
  if (isDrillthrough) {
    config.visibility = 1;
    config.type = 2;
    config.filterSortOrder = 3;
    config.keepAllFilters = false;
  }
  return config;
}

// ─── Visual container objects ─────────────────────────────────────────────────

function titleObjects(title) {
  return {
    background: [
      {
        properties: {
          show: literal("true"),
          color: color(palette.panel),
          transparency: literal("0D"),
        },
      },
    ],
    border: [
      {
        properties: {
          show: literal("true"),
          color: color(palette.border),
          radius: literal("8D"),
        },
      },
    ],
    dropShadow: [
      {
        properties: {
          show: literal("true"),
          color: color("#6FA56D"),
          transparency: literal("70D"),
          blur: literal("6D"),
          angle: literal("45D"),
          distance: literal("4D"),
        },
      },
    ],
    title: [
      {
        properties: {
          show: literal("true"),
          text: literal(`'${title}'`),
          alignment: literal("'center'"),
          bold: literal("true"),
          fontSize: literal("8D"),
          fontColor: color(palette.text),
        },
      },
    ],
  };
}

// ─── Query builders ───────────────────────────────────────────────────────────

function source(table) {
  return table
    .split("_")
    .map((item) => item[0])
    .join("")
    .slice(0, 8);
}

function column(table, property, displayName = property) {
  const src = source(table);
  return {
    queryRef: `${table}.${property}`,
    select: {
      Column: {
        Expression: { SourceRef: { Source: src } },
        Property: property,
      },
      Name: `${table}.${property}`,
      NativeReferenceName: displayName,
    },
  };
}

function aggregation(table, property, operation, displayName) {
  const functions = { Sum: 0, Avg: 1, Count: 2, Min: 3, Max: 4 };
  const src = source(table);
  return {
    queryRef: `${operation}(${table}.${property})`,
    select: {
      Aggregation: {
        Expression: {
          Column: {
            Expression: { SourceRef: { Source: src } },
            Property: property,
          },
        },
        Function: functions[operation],
      },
      Name: `${operation}(${table}.${property})`,
      NativeReferenceName: displayName,
    },
  };
}

function measure(table, property, displayName = property) {
  const src = source(table);
  return {
    queryRef: `${table}.${property}`,
    select: {
      Measure: {
        Expression: { SourceRef: { Source: src } },
        Property: property,
      },
      Name: `${table}.${property}`,
      NativeReferenceName: displayName,
    },
  };
}

function query(table, fields, orderField = null, sortDesc = true) {
  const result = {
    Version: 2,
    From: [{ Name: source(table), Entity: table, Type: 0 }],
    Select: fields.map((field) => field.select),
  };
  if (orderField) {
    const expression =
      orderField.select.Aggregation || orderField.select.Column || orderField.select.Measure;
    result.OrderBy = [{ Direction: sortDesc ? 2 : 1, Expression: expression }];
  }
  return result;
}

// ─── Container wrapper ────────────────────────────────────────────────────────

function container(name, z, x, y, width, height, singleVisual) {
  const id = crypto.randomBytes(10).toString("hex");
  return {
    folder: `${String(z).padStart(5, "0")}_${name}`,
    config: {
      name: id,
      layouts: [{ id: 0, position: { x, y, z, width, height, tabOrder: z } }],
      singleVisual,
    },
    visualContainer: { height, tabOrder: z, width, x, y, z },
  };
}

// ─── Visual builders ──────────────────────────────────────────────────────────

function shape(name, z, x, y, width, height, fillColor, radius = 8, transparency = 0) {
  return container(name, z, x, y, width, height, {
    visualType: "shape",
    drillFilterOtherVisuals: true,
    objects: {
      shape: [{ properties: { tileShape: literal("'rectangleRounded'") } }],
      fill: [
        {
          properties: {
            transparency: literal(`${transparency}D`),
            fillColor: color(fillColor),
          },
          selector: { id: "default" },
        },
      ],
      outline: [
        {
          properties: {
            show: literal("true"),
            lineColor: color(fillColor),
            weight: literal("1D"),
            roundEdge: literal(`${radius}D`),
          },
          selector: { id: "default" },
        },
      ],
    },
  });
}

// Colored section-header strip with white label (centered)
function sectionBand(name, z, x, y, width, height, label) {
  return container(name, z, x, y, width, height, {
    visualType: "textbox",
    drillFilterOtherVisuals: true,
    objects: {
      general: [
        {
          properties: {
            paragraphs: [
              {
                textRuns: [
                  {
                    value: label,
                    textStyle: {
                      fontWeight: "bold",
                      fontSize: "8pt",
                      color: palette.white,
                    },
                  },
                ],
                horizontalAlignment: "Center",
              },
            ],
          },
        },
      ],
    },
    vcObjects: {
      background: [
        {
          properties: {
            show: literal("true"),
            color: color(palette.accentMuted),
            transparency: literal("0D"),
          },
        },
      ],
      border: [{ properties: { show: literal("false") } }],
    },
  });
}

function textbox(name, z, x, y, width, height, text, size, colorValue, bold = true) {
  return container(name, z, x, y, width, height, {
    visualType: "textbox",
    drillFilterOtherVisuals: true,
    objects: {
      general: [
        {
          properties: {
            paragraphs: [
              {
                textRuns: [
                  {
                    value: text,
                    textStyle: {
                      fontWeight: bold ? "bold" : "normal",
                      fontSize: `${size}pt`,
                      color: colorValue,
                    },
                  },
                ],
              },
            ],
          },
        },
      ],
    },
    vcObjects: {
      background: [{ properties: { show: literal("false") } }],
    },
  });
}

function infoBox(name, z, x, y, width, height, title, lines) {
  const paragraphs = [
    {
      textRuns: [
        {
          value: title,
          textStyle: { fontWeight: "bold", fontSize: "11pt", color: palette.white },
        },
      ],
      horizontalAlignment: "Center",
    },
    {
      textRuns: [{ value: "", textStyle: { fontSize: "4pt", color: palette.white } }],
    },
    ...lines.map((line) => ({
      textRuns: [
        {
          value: `• ${line}`,
          textStyle: { fontWeight: "normal", fontSize: "8pt", color: "#E6F2E8" },
        },
      ],
      spaceAfter: 2,
    })),
  ];
  return container(name, z, x, y, width, height, {
    visualType: "textbox",
    drillFilterOtherVisuals: true,
    objects: { general: [{ properties: { paragraphs } }] },
    vcObjects: {
      background: [
        {
          properties: {
            show: literal("true"),
            color: color(palette.header),
            transparency: literal("0D"),
          },
        },
      ],
      border: [
        {
          properties: {
            show: literal("true"),
            color: color(palette.accentMuted),
            radius: literal("8D"),
          },
        },
      ],
    },
  });
}

function cardMeasure(
  name,
  z,
  x,
  y,
  width,
  height,
  table,
  measureName,
  title,
  formatString = null,
  labelSize = 18,
  precision = 1,
  scale = "1D",
) {
  const value = measure(table, measureName, title);
  const columnProperties = { [value.queryRef]: { displayName: title } };
  if (formatString) columnProperties[value.queryRef].formatString = formatString;

  return container(name, z, x, y, width, height, {
    visualType: "card",
    projections: { Values: [{ queryRef: value.queryRef }] },
    prototypeQuery: query(table, [value], value),
    columnProperties,
    drillFilterOtherVisuals: true,
    hasDefaultSort: true,
    objects: {
      categoryLabels: [{ properties: { show: literal("false") } }],
      labels: [
        {
          properties: {
            fontSize: literal(`${labelSize}D`),
            color: color(palette.accent),
            labelDisplayUnits: literal(scale),
            labelPrecision: literal(`${precision}D`),
          },
        },
      ],
    },
    vcObjects: titleObjects(title),
  });
}

// Generic chart — works for clusteredBarChart, clusteredColumnChart, lineChart
function chartMeasure(
  name,
  z,
  x,
  y,
  width,
  height,
  visualType,
  table,
  categoryField,
  measureName,
  title,
  valueFormat = null,
  scale = "1D",
  extraObjects = {},
) {
  const category = column(table, categoryField);
  const value = measure(table, measureName, title);
  const columnProperties = {
    [category.queryRef]: { displayName: categoryField },
    [value.queryRef]: { displayName: title },
  };
  if (valueFormat) columnProperties[value.queryRef].formatString = valueFormat;

  const isLine = visualType === "lineChart";

  return container(name, z, x, y, width, height, {
    visualType,
    projections: {
      Category: [{ queryRef: category.queryRef, suppressConcat: false }],
      Y: [{ queryRef: value.queryRef }],
    },
    prototypeQuery: query(table, [category, value], isLine ? null : value),
    columnProperties,
    drillFilterOtherVisuals: true,
    hasDefaultSort: true,
    objects: {
      categoryAxis: [
        {
          properties: {
            show: literal("true"),
            showAxisTitle: literal("false"),
            showTitle: literal("false"),
            labelColor: color(palette.muted),
            fontSize: literal("8D"),
            labelDisplayUnits: literal("1D"),
          },
        },
      ],
      valueAxis: [
        {
          properties: {
            show: literal("true"),
            showAxisTitle: literal("false"),
            showTitle: literal("false"),
            labelColor: color(palette.muted),
            fontSize: literal("8D"),
            labelDisplayUnits: literal(scale),
          },
        },
      ],
      labels: [
        {
          properties: {
            show: literal(isLine ? "false" : "true"),
            fontSize: literal("8D"),
            color: color(palette.text),
            labelDisplayUnits: literal(scale),
            labelPrecision: literal("1D"),
            position: literal("'OutsideEnd'"),
          },
        },
      ],
      dataPoint: [
        {
          properties: {
            defaultColor: color(palette.accent),
          },
        },
      ],
      ...(isLine
        ? {
            line: [
              {
                properties: {
                  strokeWidth: literal("2D"),
                },
              },
            ],
            fillPoint: [{ properties: { show: literal("true") } }],
          }
        : {}),
      ...extraObjects,
    },
    vcObjects: titleObjects(title),
  });
}

function donut(name, z, x, y, width, height, table, categoryField, countField, title, legendTitle = null) {
  const category = column(table, categoryField);
  const value = aggregation(table, countField, "Count", "Kayit Sayisi");
  return withFilters(container(name, z, x, y, width, height, {
    visualType: "donutChart",
    projections: {
      Category: [{ queryRef: category.queryRef }],
      Y: [{ queryRef: value.queryRef }],
    },
    prototypeQuery: query(table, [category, value], value),
    columnProperties: {
      [category.queryRef]: { displayName: categoryField },
      [value.queryRef]: { displayName: "Kayit Sayisi", formatString: "#,0" },
    },
    drillFilterOtherVisuals: true,
    hasDefaultSort: true,
    objects: {
      legend: [
        {
          properties: {
            show: literal("true"),
            position: literal("'RightCenter'"),
            labelColor: color(palette.muted),
            fontSize: literal("8D"),
            ...(legendTitle ? {
              showTitle: literal("true"),
              titleText: literal(`'${legendTitle}'`),
            } : {}),
          },
        },
      ],
      labels: [
        {
          properties: {
            show: literal("true"),
            color: color(palette.muted),
            labelStyle: literal("'Category, percent of total'"),
            fontSize: literal("8D"),
          },
        },
      ],
    },
    vcObjects: titleObjects(title),
  }), notBlankFilter(table, categoryField));
}

function tableVisual(name, z, x, y, width, height, table, columns, title, sortFieldName = null, sortDesc = true) {
  const fields = columns.map(([property, displayName, formatString]) => ({
    ...column(table, property, displayName),
    displayName,
    formatString,
  }));
  const columnProperties = Object.fromEntries(
    fields.map((field) => [
      field.queryRef,
      { displayName: field.displayName, formatString: field.formatString || null },
    ]),
  );
  const sortField = sortFieldName
    ? fields.find((f) => f.queryRef === `${table}.${sortFieldName}`)
    : null;
  return container(name, z, x, y, width, height, {
    visualType: "tableEx",
    projections: { Values: fields.map((field) => ({ queryRef: field.queryRef })) },
    prototypeQuery: query(table, fields, sortField || null, sortDesc),
    columnProperties,
    drillFilterOtherVisuals: true,
    objects: {
      columnHeaders: [
        {
          properties: {
            backColor: color(palette.header),
            fontColor: color(palette.white),
            bold: literal("true"),
            fontSize: literal("8D"),
            wordWrap: literal("true"),
          },
        },
      ],
      values: [
        {
          properties: {
            fontSize: literal("8D"),
            fontColorPrimary: color(palette.text),
            fontColorSecondary: color(palette.text),
            backColorPrimary: color(palette.panel),
            backColorSecondary: color(palette.panelAlt),
          },
        },
      ],
      grid: [
        {
          properties: {
            gridVertical: literal("false"),
            gridHorizontal: literal("true"),
            gridHorizontalColor: color(palette.border),
            rowPadding: literal("3D"),
          },
        },
      ],
      total: [{ properties: { totals: literal("false") } }],
    },
    vcObjects: titleObjects(title),
  });
}

function slicer(name, z, x, y, width, height, table, property, title, searchEnabled = false) {
  const field = column(table, property, title);
  return withFilters(container(name, z, x, y, width, height, {
    visualType: "slicer",
    projections: { Values: [{ queryRef: field.queryRef, active: true }] },
    prototypeQuery: query(table, [field]),
    columnProperties: { [field.queryRef]: { displayName: title } },
    drillFilterOtherVisuals: true,
    objects: {
      data: [{ properties: { mode: literal("'Dropdown'"), ...(searchEnabled ? { searchEnabled: literal("true") } : {}) } }],
      selection: [
        {
          properties: {
            singleSelect: literal("false"),
            selectAllCheckboxEnabled: literal("true"),
          },
        },
      ],
      items: [
        {
          properties: {
            textSize: literal("8D"),
            fontColor: color(palette.text),
            background: color(palette.panel),
          },
        },
      ],
      header: [
        {
          properties: {
            show: literal("true"),
            fontColor: color(palette.header),
            background: color(palette.panelAlt),
            textSize: literal("10D"),
          },
        },
      ],
    },
    vcObjects: titleObjects(title),
  }), notBlankFilter(table, property));
}

// Card backed by a direct column aggregation (no pre-built measure required)
function cardAgg(name, z, x, y, width, height, table, property, operation, title, formatString = null, labelSize = 18, precision = 1, scale = "1D") {
  const value = aggregation(table, property, operation, title);
  const columnProperties = { [value.queryRef]: { displayName: title } };
  if (formatString) columnProperties[value.queryRef].formatString = formatString;
  return container(name, z, x, y, width, height, {
    visualType: "card",
    projections: { Values: [{ queryRef: value.queryRef }] },
    prototypeQuery: query(table, [value], value),
    columnProperties,
    drillFilterOtherVisuals: true,
    hasDefaultSort: true,
    objects: {
      categoryLabels: [{ properties: { show: literal("false") } }],
      labels: [
        {
          properties: {
            fontSize: literal(`${labelSize}D`),
            color: color(palette.accent),
            labelDisplayUnits: literal(scale),
            labelPrecision: literal(`${precision}D`),
          },
        },
      ],
    },
    vcObjects: titleObjects(title),
  });
}

function panel(name, z, x, y, width, height) {
  return shape(name, z, x, y, width, height, "#DDF3D8", 8, 16);
}

function backButton(name, z, x, y, width, height) {
  return container(name, z, x, y, width, height, {
    visualType: "actionButton",
    drillFilterOtherVisuals: true,
    objects: {
      icon: [
        {
          properties: { shapeType: literal("'back'"), lineColor: color(palette.white) },
          selector: { id: "default" },
        },
      ],
      text: [
        { properties: { show: literal("true") } },
        {
          properties: {
            text: literal("'Geri'"),
            fontColor: color(palette.white),
            bold: literal("true"),
            fontSize: literal("10D"),
          },
          selector: { id: "default" },
        },
      ],
      fill: [
        {
          properties: {
            fillColor: color(palette.accentDark),
            transparency: literal("0D"),
          },
          selector: { id: "default" },
        },
      ],
      outline: [{ properties: { show: literal("false") } }],
    },
    vcObjects: {
      visualLink: [
        { properties: { show: literal("true"), type: literal("'Back'") } },
      ],
    },
  });
}

// ─── Page utilities ───────────────────────────────────────────────────────────

function setShapeFill(pagePath, prefix, fillColor) {
  const root = path.join(pagePath, "visualContainers");
  const entry = fs.readdirSync(root).find((name) => name.startsWith(prefix));
  if (!entry) return;
  const configPath = path.join(root, entry, "config.json");
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  config.singleVisual.objects.fill = [
    {
      properties: {
        transparency: literal("0D"),
        fillColor: color(fillColor),
      },
      selector: { id: "default" },
    },
  ];
  writeJson(configPath, config);
}

function styleMainPage(pagePath) {
  setShapeFill(pagePath, "04000_", palette.header);
  setShapeFill(pagePath, "08000_", "#E6FF00");
  setShapeFill(pagePath, "09000_", palette.header);
}

function writeVisual(pagePath, visual) {
  const target = path.join(pagePath, "visualContainers", visual.folder);
  fs.mkdirSync(target, { recursive: true });
  writeJson(path.join(target, "config.json"), visual.config);
  writeJson(path.join(target, "visualContainer.json"), visual.visualContainer);
  writeJson(path.join(target, "filters.json"), visual.filters || []);
}

function clearGenerated(pagePath) {
  const root = path.join(pagePath, "visualContainers");
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (entry.isDirectory() && Number.parseInt(entry.name.slice(0, 5), 10) >= 10000) {
      fs.rmSync(path.join(root, entry.name), { recursive: true, force: true });
    }
  }
}

function clearAllVisuals(pagePath) {
  const root = path.join(pagePath, "visualContainers");
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      fs.rmSync(path.join(root, entry.name), { recursive: true, force: true });
    }
  }
}

function drillthroughFilters(table, property) {
  return [
    {
      name: `Drillthrough_${table}_${property}`,
      expression: {
        Column: {
          Expression: { SourceRef: { Entity: table } },
          Property: property,
        },
      },
      type: "Categorical",
      howCreated: 5,
      ordinal: 0,
    },
  ];
}

function notBlankFilter(table, property) {
  return {
    name: `NotBlank_${table.replace(/[^A-Za-z0-9]/g, "_").slice(0, 24)}_${property}`,
    expression: {
      Not: {
        Expression: {
          IsEmpty: {
            Expression: {
              Column: {
                Expression: { SourceRef: { Entity: table } },
                Property: property,
              },
            },
          },
        },
      },
    },
    type: "Advanced",
    howCreated: 0,
  };
}

function withFilters(visual, ...filters) {
  return { ...visual, filters: [...(visual.filters || []), ...filters] };
}

function writeDetailPageShell(pagePath, table, property) {
  writeJson(path.join(pagePath, "config.json"), pageConfig(true));
  writeJson(path.join(pagePath, "filters.json"), drillthroughFilters(table, property));
}

// ─── Layout constants ─────────────────────────────────────────────────────────
//
//  Main pages (005, 006) share this grid:
//
//  Left sidebar (existing):  x = 0 .. 95
//  Content area:             x = 105 .. 975   (w = 870)
//  Filter panel:             x = 975 .. 1265  (w = 290)
//
//  Vertical zones:
//    Header (existing):      y = 0  .. 65
//    KPI section band:       y = 78  h = 18
//    KPI cards:              y = 100  h = 78
//    Analysis section band:  y = 188  h = 18
//    Main charts:            y = 210  h = 230
//    Outcome section band:   y = 448  h = 18
//    Bottom visuals:         y = 470  h = 228
//
//  5 KPI cards (w=170 each, gap=5):
//    x positions: 105, 280, 455, 630, 805  (total = 875 ... fits in 870+5 padding)

const CX = 105;   // content start x
const CW = 870;   // content width
const FX = 975;   // filter panel start x
const FW = 290;   // filter panel width
const FY = 78;    // filter panel top y
const FH = 618;   // filter panel height

const CARD_W = 170;
const CARD_H = 86;
const CARD_Y = 104;
const CARD_GAP = 5;
const FILTER_TITLE_H = 30;   // FİLTRELER header textbox height
const FILTER_FIRST_Y = 122;  // first slicer y inside filter panel

function cardX(n) {
  return CX + n * (CARD_W + CARD_GAP);
}

// ─── PAGE 005 — Transfer ve Piyasa Değeri Analizi ────────────────────────────

function buildTransferPage() {
  const T = "fct_transfer_market_value_analysis";

  const visuals = [
    // Title + subtitle --------------------------------------------------------
    textbox(
      "Page Title", 10000,
      310, 12, 680, 40,
      "Transfer ve Piyasa Değeri Analizi", 20, palette.white,
    ),
    textbox(
      "Page Subtitle", 10050,
      310, 52, 680, 15,
      "Tarihsel transfer ücretleri  |  Piyasa değeri hareketleri  |  Sezon & pozisyon analizi",
      7.5, "#C8F5C0", false,
    ),

    // KPI section band --------------------------------------------------------
    sectionBand("KPI Band", 10200, CX, FY, CW, 22, "ANAHTAR GÖSTERGELER"),

    // 5 KPI cards
    cardMeasure("Transfer Count Card", 12000, cardX(0), CARD_Y, CARD_W, CARD_H,
      T, "Transfer Count", "Transfer Sayısı", null, 18, 0),
    cardMeasure("Known Fee Card", 13000, cardX(1), CARD_Y, CARD_W, CARD_H,
      T, "Known Fee Coverage %", "Bilinen Ücret %", null, 18, 1),
    cardMeasure("Avg Fee Card", 14000, cardX(2), CARD_Y, CARD_W, CARD_H,
      T, "Average Known Transfer Fee", "Ort. Ücret", null, 18, 1, "1000000D"),
    cardMeasure("Fee Premium Card", 14500, cardX(3), CARD_Y, CARD_W, CARD_H,
      T, "Average Fee Premium Discount %", "Prim/İskonto %", null, 18, 1),
    cardMeasure("Total Fee Card", 15000, cardX(4), CARD_Y, CARD_W, CARD_H,
      T, "Total Known Transfer Fee", "Toplam Hacim", null, 18, 1, "1000000D"),

    // Analysis section band ---------------------------------------------------
    sectionBand("Analysis Band", 15500, CX, 186, CW, 22, "PİYASA DEĞERİ ANALİZİ"),

    // Main charts (y=212, h=230)
    chartMeasure(
      "Fee Premium by Position", 16000,
      CX, 212, 425, 230,
      "clusteredBarChart",
      T, "pozisyon_tr",
      "Average Fee Premium Discount %",
      "Prim/İskonto % (Poz.)", null,
    ),
    chartMeasure(
      "Transfer Fee by Season", 17000,
      CX + 440, 212, 425, 230,
      "clusteredColumnChart",
      T, "transfer_season",
      "Average Known Transfer Fee",
      "Ort. Ücret (Sezon)", null, "1000000D",
    ),

    // Outcome section band ----------------------------------------------------
    sectionBand("Outcome Band", 17500, CX, 446, CW, 22, "TRANSFER SONUCU ANALİZİ"),

    // Bottom row (y=470, h=228)
    donut(
      "Post Transfer Direction", 18000,
      CX, 470, 235, 228,
      T, "yon_etiketi_tr", "transfer_key",
      "Değer Yönü", "Değer Yönü",
    ),
    chartMeasure(
      "Volume by Position", 18500,
      CX + 248, 470, 248, 228,
      "clusteredColumnChart",
      T, "pozisyon_tr",
      "Transfer Count",
      "Transfer Hacmi", null,
    ),
    tableVisual(
      "Transfer Detail Table", 19000,
      CX + 508, 470, 362, 225,
      T,
      [
        ["player_name", "Oyuncu", null],
        ["from_club_name", "Kaynak Kulüp", null],
        ["to_club_name", "Hedef Kulüp", null],
        ["transfer_fee", "Transfer Ücreti", "€#,0"],
        ["market_value_baseline", "Piyasa Değeri", "€#,0"],
        ["fee_market_value_difference_pct", "Prim %", "0.0"],
        ["yon_etiketi_tr", "Sonraki Yön", null],
      ],
      "Kayıt Listesi",
      "transfer_fee",
    ),

    // Filter panel ------------------------------------------------------------
    panel("Filter Panel BG", 10500, FX, FY, FW, FH),
    textbox("Filter Title", 11000, FX + 15, FY + 10, FW - 30, FILTER_TITLE_H, "FİLTRELER", 8, palette.header),

    slicer("Season Slicer", 20000, FX + 10, FILTER_FIRST_Y, FW - 20, 52, T, "transfer_season", "Transfer Sezonu"),
    slicer("Position Slicer", 21000, FX + 10, FILTER_FIRST_Y + 62, FW - 20, 52, T, "pozisyon_tr", "Pozisyon"),
    slicer("Fee Status Slicer", 22000, FX + 10, FILTER_FIRST_Y + 124, FW - 20, 52, T, "fee_status", "Ücret Durumu"),
    slicer("Direction Slicer", 23000, FX + 10, FILTER_FIRST_Y + 186, FW - 20, 52, T, "yon_etiketi_tr", "Değer Yönü"),

    cardMeasure("Context Card", 24000, FX + 10, FILTER_FIRST_Y + 248, FW - 20, 56,
      T, "Transfer Context Summary", "Aktif Seçim", null, 8, 0),

    infoBox("Governance Box", 25000, FX + 10, FILTER_FIRST_Y + 314, FW - 20, 256, "ANALİTİK BULGULAR", [
      "Transferlerin ~%60'ı piyasa değerinin altında gerçekleşir — kulüpler sistematik olarak iskontolu alım yapar.",
      "Forvetler prim, kaleciler iskonto ile transfer edilir: pozisyon, fiyatlamayı doğrudan belirler.",
      "2016–2020 zirve döneminin ardından transfer bütçeleri daralma eğilimindedir.",
      "'Değer Arttı' filtresi: gerçekten değer yaratan transferleri izole edin.",
      "Yüksek prim transferler (>%30) çoğunlukla yıldız oyuncu veya rekabetçi teklif durumlarıdır.",
    ]),
  ];

  clearGenerated(pages.transfer);
  styleMainPage(pages.transfer);
  visuals.forEach((v) => writeVisual(pages.transfer, v));
}

// ─── PAGE 006 — Oyuncu Piyasa Değeri Tahmini ─────────────────────────────────

function buildMlPage() {
  const T = "ml_player_market_value_current_predictions";

  const visuals = [
    // Title + subtitle --------------------------------------------------------
    textbox(
      "ML Title", 10000,
      310, 12, 680, 40,
      "Oyuncu Piyasa Değeri Tahmini", 20, palette.white,
    ),
    textbox(
      "ML Subtitle", 10050,
      310, 52, 680, 15,
      "ML v5 Ensemble  |  R2=0.976, WAPE=%12.5  |  %90 güven aralığı  |  Kalite tabanlı yönlendirme",
      7.5, "#C8F5C0", false,
    ),

    // KPI section band --------------------------------------------------------
    sectionBand("KPI Band", 10200, CX, FY, CW, 22, "ANAHTAR GÖSTERGELER"),

    // 5 KPI cards
    cardMeasure("Scored Players Card", 12000, cardX(0), CARD_Y, CARD_W, CARD_H,
      T, "Scored Player Count", "Tahmin Oyuncusu", null, 18, 0),
    cardMeasure("Decision Ready Card", 13000, cardX(1), CARD_Y, CARD_W, CARD_H,
      T, "Decision Ready Rate %", "Karar Hazır %", null, 18, 1),
    cardMeasure("Avg Prediction Card", 14000, cardX(2), CARD_Y, CARD_W, CARD_H,
      T, "Average Predicted Market Value", "Ort. Tahmin", null, 18, 1, "1000000D"),
    cardMeasure("Avg Previous Card", 14500, cardX(3), CARD_Y, CARD_W, CARD_H,
      T, "Average Previous Market Value", "Ort. Önceki", null, 18, 1, "1000000D"),
    cardMeasure("Upside Pct Card", 15000, cardX(4), CARD_Y, CARD_W, CARD_H,
      T, "Average Prediction Upside %", "Değer Artışı %", null, 18, 1),

    // Analysis section band ---------------------------------------------------
    sectionBand("Analysis Band", 15500, CX, 186, CW, 22, "TAHMİN ANALİZİ"),

    // Main charts: bar + donut (y=212, h=230)
    chartMeasure(
      "Prediction by Position", 16000,
      CX, 212, 530, 230,
      "clusteredBarChart",
      T, "pozisyon_tr",
      "Average Predicted Market Value",
      "Tahmin Değeri (Poz.)", null, "1000000D",
    ),
    donut(
      "Quality Distribution", 17000,
      CX + 545, 212, 320, 230,
      T, "kalite_etiketi_tr", "scoring_row_key",
      "Kalite Dağılımı", "Tahmin Kalitesi",
    ),

    // Player list section band ------------------------------------------------
    sectionBand("Player Band", 17500, CX, 446, CW, 22, "OYUNCU TAHMİN LİSTESİ"),

    // Bottom row: upside bar + table (y=470, h=225)
    chartMeasure(
      "Upside by Position", 18000,
      CX, 470, 340, 225,
      "clusteredBarChart",
      T, "pozisyon_tr",
      "Average Prediction Upside %",
      "Tahmin Artışı % (Poz.)", null, "1D",
      {
        referenceLine: [
          {
            properties: {
              show: literal("true"),
              type: literal("'Constant'"),
              value: literal("0D"),
              label: literal("'%0 Eşik'"),
              color: { solid: { color: { expr: { Literal: { Value: "'#E63946'" } } } } },
              lineStyle: literal("'dashed'"),
              transparency: literal("40D"),
            },
          },
        ],
      },
    ),
    tableVisual(
      "Prediction Detail Table", 19000,
      CX + 353, 470, 512, 225,
      T,
      [
        ["player_name", "Oyuncu", null],
        ["pozisyon_tr", "Poz.", null],
        ["kalite_etiketi_tr", "Kalite", null],
        ["previous_market_value_eur", "Önceki", "€#,0"],
        ["predicted_market_value_eur", "Tahmin", "€#,0"],
        ["prediction_delta_vs_previous_pct", "Fark %", "0.0"],
        ["prediction_lower_eur", "Alt Sınır", "€#,0"],
        ["prediction_upper_eur", "Üst Sınır", "€#,0"],
      ],
      "Tahmin Listesi",
      "prediction_delta_vs_previous_pct",
    ),

    // Filter panel ------------------------------------------------------------
    panel("ML Filter Panel BG", 10500, FX, FY, FW, FH),
    textbox("ML Filter Title", 11000, FX + 15, FY + 10, FW - 30, FILTER_TITLE_H, "FİLTRELER", 8, palette.header),

    slicer("ML Position Slicer", 20000, FX + 10, FILTER_FIRST_Y, FW - 20, 52, T, "pozisyon_tr", "Pozisyon"),
    slicer("ML Quality Slicer", 21000, FX + 10, FILTER_FIRST_Y + 62, FW - 20, 52, T, "kalite_etiketi_tr", "Tahmin Kalitesi"),
    slicer("ML Country Slicer", 22000, FX + 10, FILTER_FIRST_Y + 124, FW - 20, 52, T, "competition_country_name", "Rekabet Ülkesi", true),
    slicer("ML Foot Slicer", 23000, FX + 10, FILTER_FIRST_Y + 186, FW - 20, 52, T, "preferred_foot", "Dominant Ayak"),

    cardMeasure("ML Context Card", 24000, FX + 10, FILTER_FIRST_Y + 248, FW - 20, 56,
      T, "Prediction Context Summary", "Aktif Seçim", null, 8, 0),

    infoBox("ML Governance Box", 25000, FX + 10, FILTER_FIRST_Y + 314, FW - 20, 256, "ANALİTİK BULGULAR", [
      "Forvetler en yüksek piyasa değerini taşır; model bu eşitsizliği pozisyon bazında doğru yakalar.",
      "'Karar Hazır %' oranı, modelin güvenilir tahmin ürettiği oyuncu kapsamını gösterir.",
      "Kırmızı referans çizgisinin solundaki pozisyonlar ortalama değer kaybı riski taşır.",
      "Tahmin kalitesi 'Yüksek' filtresi: müzakereler için en güvenilir veri tabanını izole eder.",
      "Dar güven aralığı = modelin o oyuncuya yüksek özgüveni; geniş aralık = daha fazla belirsizlik.",
    ]),
  ];

  clearGenerated(pages.ml);
  styleMainPage(pages.ml);
  visuals.forEach((v) => writeVisual(pages.ml, v));
}

// ─── PAGE 008 — Transfer Player Detail (drill-through) ───────────────────────

function buildTransferDetailPage() {
  const T = "fct_transfer_market_value_analysis";

  const visuals = [
    // Frame
    shape("Detail BG", 0, 0, 0, 1280, 720, palette.page, 0, 0),
    shape("Detail Header", 100, 0, 0, 1280, 65, palette.header, 0, 0),
    backButton("Back Button", 200, 15, 14, 100, 38),
    textbox("Detail Title", 300, 300, 14, 680, 38, "Transfer Oyuncu Detayı", 18, palette.white),

    // KPI strip (y=73)
    sectionBand("KPI Band", 10000, 105, 73, 1060, 18, "OYUNCU ÖZETİ"),
    cardMeasure("Player Name Card", 10100, 105, 95, 415, 72,
      T, "Selected Transfer Player", "Seçili Oyuncu", null, 12, 0),
    cardMeasure("Transfer Count Card", 10200, 530, 95, 195, 72,
      T, "Transfer Count", "Transfer Sayısı", null, 16, 0),
    cardMeasure("Total Fee Card", 10300, 735, 95, 210, 72,
      T, "Total Known Transfer Fee", "Toplam Bilinen Ücret", null, 16, 1, "1000000D"),
    cardMeasure("Avg Outcome Card", 10400, 955, 95, 210, 72,
      T, "Average Post Transfer Value Change %", "Ort. Sonraki Değişim", null, 16, 1),

    // Charts (y=175)
    sectionBand("Analysis Band", 11000, 105, 175, 1060, 18, "TRANSFER ANALİZİ"),
    chartMeasure(
      "Fee Timeline", 11100,
      105, 197, 510, 252,
      "clusteredColumnChart",
      T, "transfer_season",
      "Average Known Transfer Fee",
      "Ücret (Sezon)", null, "1000000D",
    ),
    donut(
      "Direction Donut", 11200,
      625, 197, 255, 252,
      T, "yon_etiketi_tr", "transfer_key",
      "Değer Yönü", "Değer Yönü",
    ),
    infoBox("Detail Info", 11300, 890, 197, 275, 252, "OYUNCU ANALİZİ", [
      "Toplam ücret ve ortalama sonraki değişim, oyuncunun yarattığı net değeri özetler.",
      "Sezon bazlı ücret trendi: oyuncunun müzakere gücünü ve piyasa algısını yansıtır.",
      "Prim (+%): kulübün o oyuncuya standart değerinin üstünde ödediğini gösterir.",
      "Sonraki değişim % negatifse oyuncu, transferden sonra piyasa değeri kaybetmiştir.",
    ]),

    // Full-width table (y=457)
    sectionBand("History Band", 12000, 105, 457, 1060, 18, "TAM TRANSFER GEÇMİŞİ"),
    tableVisual(
      "Transfer History Table", 12100,
      105, 479, 1060, 218,
      T,
      [
        ["player_name", "Oyuncu", null],
        ["transfer_season", "Sezon", null],
        ["from_club_name", "Kaynak Kulüp", null],
        ["to_club_name", "Hedef Kulüp", null],
        ["transfer_fee", "Transfer Ücreti", "€#,0"],
        ["market_value_baseline", "Baseline Değer", "€#,0"],
        ["fee_market_value_difference_pct", "Prim / İskonto %", "0.0"],
        ["market_value_change_after_transfer_pct", "Sonraki Değişim %", "0.0"],
      ],
      "Oyuncu Transfer Geçmişi — Tüm Sezonlar",
    ),
  ];

  clearAllVisuals(pages.transferDetail);
  writeDetailPageShell(pages.transferDetail, T, "player_name");
  visuals.forEach((v) => writeVisual(pages.transferDetail, v));
}

// ─── PAGE 009 — ML Player Detail (drill-through) ─────────────────────────────

function buildMlDetailPage() {
  const T = "ml_player_market_value_current_predictions";

  const visuals = [
    // Frame
    shape("Detail BG", 0, 0, 0, 1280, 720, palette.page, 0, 0),
    shape("Detail Header", 100, 0, 0, 1280, 65, palette.header, 0, 0),
    backButton("Back Button", 200, 15, 14, 100, 38),
    textbox("Detail Title", 300, 300, 14, 680, 38, "Oyuncu Piyasa Değeri Tahmin Detayı", 18, palette.white),

    // KPI strip (y=73)
    sectionBand("KPI Band", 10000, 105, 73, 1060, 18, "OYUNCU ÖZETİ"),
    cardMeasure("Player Name Card", 10100, 105, 95, 375, 72,
      T, "Selected Prediction Player", "Seçili Oyuncu", null, 12, 0),
    cardMeasure("Previous Value Card", 10200, 490, 95, 205, 72,
      T, "Average Previous Market Value", "Önceki Değer", null, 15, 1, "1000000D"),
    cardMeasure("Predicted Value Card", 10300, 705, 95, 205, 72,
      T, "Average Predicted Market Value", "Tahmin Değeri", null, 15, 1, "1000000D"),
    cardMeasure("Upside Card", 10400, 920, 95, 245, 72,
      T, "Average Prediction Upside %", "Tahmin Farkı %", null, 15, 1),

    // Charts (y=175)
    sectionBand("Analysis Band", 11000, 105, 175, 1060, 18, "TAHMİN ANALİZİ"),
    chartMeasure(
      "Prediction by Position", 11100,
      105, 197, 510, 252,
      "clusteredBarChart",
      T, "pozisyon_tr",
      "Average Predicted Market Value",
      "Pozisyon Tahminleri", null, "1000000D",
    ),
    donut(
      "Quality Donut", 11200,
      625, 197, 265, 252,
      T, "kalite_etiketi_tr", "scoring_row_key",
      "Kalite Dağılımı", "Tahmin Kalitesi",
    ),
    infoBox("Detail Info", 11300, 900, 197, 265, 252, "TAHMİN ANALİZİ", [
      "Pozitif 'Fark %': oyuncu piyasada henüz tam fiyatlanmamış bir büyüme potansiyeli taşır.",
      "'Limited' kalite: tahmin yalnızca yön bilgisi verir, değer kesin değildir.",
      "Dar güven aralığı, modelin o oyuncuya yüksek özgüvenini ölçer.",
      "Önceki değer ile tahmin karşılaştırması scouting kararlarında referans noktasıdır.",
      "Ana sayfaya dönmek için sol üstteki Geri butonunu kullanın.",
    ]),

    // Full-width table (y=457)
    sectionBand("Prediction Band", 12000, 105, 457, 1060, 18, "TAHMİN KAYDI — TAM DETAY"),
    tableVisual(
      "Prediction Detail Table", 12100,
      105, 479, 1060, 218,
      T,
      [
        ["player_name", "Oyuncu", null],
        ["pozisyon_tr", "Pozisyon", null],
        ["competition_country_name", "Ülke / Lig", null],
        ["previous_market_value_eur", "Önceki Değer", "€#,0"],
        ["predicted_market_value_eur", "Tahmin Değeri", "€#,0"],
        ["prediction_delta_vs_previous_pct", "Fark %", "0.0"],
        ["prediction_lower_eur", "Alt Sınır (%90)", "€#,0"],
        ["prediction_upper_eur", "Üst Sınır (%90)", "€#,0"],
        ["kalite_etiketi_tr", "Kalite", null],
        ["model_version", "Model", null],
      ],
      "Oyuncu Tahmin Kaydı — Tüm Detaylar",
    ),
  ];

  clearAllVisuals(pages.mlDetail);
  writeDetailPageShell(pages.mlDetail, T, "player_name");
  visuals.forEach((v) => writeVisual(pages.mlDetail, v));
}

// ─── PAGE 010 — ML Model Güvenilirliği ───────────────────────────────────────

function buildMlPerformancePage() {
  const FI = "ml_player_market_value_feature_importance";
  const QG = "ml_player_market_value_quality_gates";
  const EM = "ml_player_market_value_evaluation_metrics";

  const visuals = [
    // Title + subtitle --------------------------------------------------------
    textbox("Perf Title", 10000, 310, 12, 680, 40, "ML Model Güvenilirliği", 20, palette.white),
    textbox("Perf Subtitle", 10050, 310, 52, 680, 15,
      "Özellik önemi  |  Kalite kapıları  |  Segment bazlı performans metrikleri",
      7.5, "#C8F5C0", false),

    // KPI band ----------------------------------------------------------------
    sectionBand("KPI Band", 10200, CX, FY, CW, 22, "MODEL SAĞLIĞI"),

    // KPI cards: use aggregations (no TOM measure needed)
    cardAgg("Total Features Card", 12000, cardX(0), CARD_Y, CARD_W, CARD_H,
      FI, "importance_rank", "Count", "Özellik Sayısı", null, 18, 0),
    cardAgg("R2 Card", 13000, cardX(1), CARD_Y, CARD_W, CARD_H,
      EM, "r2", "Max", "En Yüksek R²", null, 18, 3),
    cardAgg("WAPE Card", 14000, cardX(2), CARD_Y, CARD_W, CARD_H,
      EM, "wape_pct", "Min", "En Düşük WAPE", "0.0", 18, 1),
    cardAgg("Within25 Card", 14500, cardX(3), CARD_Y, CARD_W, CARD_H,
      EM, "within_25_pct", "Max", "±%25 İçinde", "0.0", 18, 1),
    cardAgg("Gates Total Card", 15000, cardX(4), CARD_Y, CARD_W, CARD_H,
      QG, "gate_name", "Count", "Toplam Kapı", null, 18, 0),

    // Analysis band -----------------------------------------------------------
    sectionBand("Analysis Band", 15500, CX, 186, CW, 22, "ÖZELLİK ETKİ ANALİZİ"),

    // Feature importance + quality gates side by side (y=212, h=230)
    tableVisual(
      "Feature Importance Table", 16000,
      CX, 212, 425, 230,
      FI,
      [
        ["importance_rank", "Sıra", "0"],
        ["feature", "Özellik", null],
        ["feature_type", "Tür", null],
        ["mae_increase_eur_mean", "MAE Artışı (€)", "€#,0"],
      ],
      "Özellik Önemi",
      "importance_rank",
      false,
    ),
    tableVisual(
      "Quality Gates Table", 17000,
      CX + 440, 212, 425, 230,
      QG,
      [
        ["gate_name", "Kalite Kapısı", null],
        ["actual_value", "Gerçek Değer", "0.000"],
        ["threshold_value", "Eşik Değer", "0.000"],
        ["passed", "Geçti?", null],
        ["severity", "Önem", null],
      ],
      "Kalite Kapıları",
    ),

    // Segment section band ----------------------------------------------------
    sectionBand("Segment Band", 17500, CX, 446, CW, 22, "PERFORMANS SEGMENTİ"),

    // Evaluation metrics table full-width (y=470, h=225)
    tableVisual(
      "Eval Metrics Table", 18000,
      CX, 470, CW, 225,
      EM,
      [
        ["segment_type", "Segment Türü", null],
        ["segment_value", "Segment Değeri", null],
        ["row_count", "Kayıt", "#,0"],
        ["r2", "R²", "0.000"],
        ["wape_pct", "WAPE %", "0.0"],
        ["mae_eur", "MAE (€)", "€#,0"],
        ["within_25_pct", "±%25 İçinde", "0.0"],
        ["mae_improvement_vs_baseline_pct", "Baseline'a Göre İyileşme", "0.0%"],
      ],
      "Segment Performansı",
      "wape_pct",
      true,
    ),

    // Filter panel ------------------------------------------------------------
    panel("Perf Filter Panel BG", 10500, FX, FY, FW, FH),
    textbox("Perf Filter Title", 11000, FX + 15, FY + 10, FW - 30, FILTER_TITLE_H, "FİLTRELER", 8, palette.header),

    slicer("Model Version Slicer", 20000, FX + 10, FILTER_FIRST_Y, FW - 20, 52, FI, "model_version", "Model Versiyonu"),
    slicer("Feature Type Slicer", 21000, FX + 10, FILTER_FIRST_Y + 62, FW - 20, 52, FI, "feature_type", "Özellik Türü"),
    slicer("Segment Type Slicer", 22000, FX + 10, FILTER_FIRST_Y + 124, FW - 20, 52, EM, "segment_type", "Segment Türü"),
    slicer("Severity Slicer", 23000, FX + 10, FILTER_FIRST_Y + 186, FW - 20, 52, QG, "severity", "Önem Seviyesi"),

    infoBox("Perf Governance Box", 25000, FX + 10, FILTER_FIRST_Y + 252, FW - 20, 344, "MODEL REHBERİ", [
      "Düşük WAPE (<%15) modelin yüksek doğruluğunu gösterir.",
      "R²>0.95 güçlü açıklama gücü anlamına gelir.",
      "Önem sırası 1 = tahmin üzerinde en fazla etkisi olan özellik.",
      "Tüm blocking kalite kapıları geçilmelidir.",
      "Feature drift izlenerek model güncelleme kararı verilir.",
      "Segment performansı pozisyon bazında yorumlanabilir.",
    ]),
  ];

  clearAllVisuals(pages.mlPerformance);
  writeJson(path.join(pages.mlPerformance, "config.json"), pageConfig(false));
  writeJson(path.join(pages.mlPerformance, "filters.json"), []);
  visuals.forEach((v) => writeVisual(pages.mlPerformance, v));
}

// ─── Run ─────────────────────────────────────────────────────────────────────

buildTransferPage();
buildMlPage();
buildTransferDetailPage();
buildMlDetailPage();
buildMlPerformancePage();

console.log("Power BI market-value pages built.");
console.log("  005 Transfer Analysis    — 5 KPIs, section bands, bar + column + donut + table");
console.log("  006 ML Prediction        — 5 KPIs, section bands, bar + donut + column + table");
console.log("  008 Transfer Detail      — drill-through, KPIs, column + donut + full table");
console.log("  009 ML Detail            — drill-through, KPIs, bar + donut + full table");
console.log("  010 ML Performance       — feature importance + quality gates + segment metrics");
