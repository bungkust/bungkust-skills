(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const {
    Card, CardHeader, CardTitle, CardContent,
    Badge, Button, Input, Label
  } = SDK.components;
  const { useState } = SDK.hooks;
  const { cn } = SDK.utils;

  function GMapsScraperPage() {
    const [query, setQuery] = useState("coffee shop");
    const [daerah, setDaerah] = useState("Yogyakarta");
    const [maxResults, setMaxResults] = useState("50");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    function scrape() {
      if (!query.trim() || !daerah.trim()) return;
      setLoading(true);
      setError(null);
      setResults(null);

      SDK.fetchJSON("/api/plugins/google-maps-scraper/scrape?" + new URLSearchParams({
        query: query,
        daerah: daerah,
        max_results: maxResults
      }))
        .then(function (data) {
          if (data.success) {
            setResults(data.results);
          } else {
            setError(data.error || "Unknown error");
          }
        })
        .catch(function (err) {
          setError("Request failed: " + err.message);
        })
        .finally(function () {
          setLoading(false);
        });
    }

    function StarRating(rating) {
      if (!rating) return React.createElement("span", { className: "text-muted-foreground" }, "-");
      const stars = "★".repeat(Math.floor(rating));
      return React.createElement("span", null,
        React.createElement("span", { className: "text-yellow-500" }, stars),
        React.createElement("span", { className: "text-muted-foreground ml-1" }, rating)
      );
    }

    function exportCSV() {
      if (!results || !results.length) return;
      var fields = ["Name", "Rating", "Reviews", "Category", "Price_range", "Address"];
      var header = fields.join(",");
      var rows = results.map(function(place) {
        return fields.map(function(f) {
          var val = (place[f] || "").toString();
          if (val.indexOf(",") !== -1 || val.indexOf('"') !== -1 || val.indexOf("\n") !== -1) {
            val = '"' + val.replace(/"/g, '""') + '"';
          }
          return val;
        }).join(",");
      });
      var csv = [header].concat(rows).join("\n");
      var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      var url = URL.createObjectURL(blob);
      var slug = query.toLowerCase().replace(/\s+/g, "_") + "_" + daerah.toLowerCase().replace(/\s+/g, "_");
      var link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", slug + ".csv");
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }

    return React.createElement("div", { className: "flex flex-col gap-6" },

      // Header card
      React.createElement(Card, null,
        React.createElement(CardHeader, null,
          React.createElement("div", { className: "flex items-center gap-3" },
            React.createElement(CardTitle, { className: "text-lg" }, "Google Maps Scraper"),
            React.createElement(Badge, { variant: "outline" }, "v1.0.0")
          )
        ),
        React.createElement(CardContent, null,
          React.createElement("p", { className: "text-sm text-muted-foreground" },
            "Scrape Google Maps listings by daerah. Results shown in table view."
          )
        )
      ),

      // Input card
      React.createElement(Card, null,
        React.createElement(CardHeader, null,
          React.createElement(CardTitle, { className: "text-base" }, "Scraper Settings")
        ),
        React.createElement(CardContent, { className: "flex flex-col gap-4" },
          React.createElement("div", { className: "grid grid-cols-1 sm:grid-cols-3 gap-4" },
            React.createElement("div", { className: "flex flex-col gap-1.5" },
              React.createElement(Label, { htmlFor: "query-input" }, "Query"),
              React.createElement(Input, {
                id: "query-input",
                value: query,
                onChange: function (e) { setQuery(e.target.value); },
                placeholder: "e.g. coffee shop, burger"
              })
            ),
            React.createElement("div", { className: "flex flex-col gap-1.5" },
              React.createElement(Label, { htmlFor: "daerah-input" }, "Daerah"),
              React.createElement(Input, {
                id: "daerah-input",
                value: daerah,
                onChange: function (e) { setDaerah(e.target.value); },
                placeholder: "e.g. Yogyakarta, Sleman"
              })
            ),
            React.createElement("div", { className: "flex flex-col gap-1.5" },
              React.createElement(Label, { htmlFor: "max-select" }, "Max Results"),
              React.createElement("select", {
                id: "max-select",
                value: maxResults,
                onChange: function (e) { setMaxResults(e.target.value); },
                className: "flex h-9 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              },
                React.createElement("option", { value: "5" }, "5"),
                React.createElement("option", { value: "10" }, "10"),
                React.createElement("option", { value: "15" }, "15"),
                React.createElement("option", { value: "20" }, "20"),
                React.createElement("option", { value: "25" }, "25"),
                React.createElement("option", { value: "30" }, "30"),
                React.createElement("option", { value: "35" }, "35"),
                React.createElement("option", { value: "40" }, "40"),
                React.createElement("option", { value: "45" }, "45"),
                React.createElement("option", { value: "50" }, "50")
              )
            )
          ),
          React.createElement(Button, {
            onClick: scrape,
            disabled: loading || !query.trim() || !daerah.trim()
          }, loading ? "Scraping..." : "🔍 Mulai Search")
        )
      ),

      // Error display
      error && React.createElement(Card, { className: "border-destructive/50" },
        React.createElement(CardHeader, null,
          React.createElement(CardTitle, { className: "text-base text-destructive" }, "Error")
        ),
        React.createElement(CardContent, null,
          React.createElement("pre", { className: "text-xs text-destructive whitespace-pre-wrap" }, error)
        )
      ),

      // Results card with native HTML table
      results && React.createElement(Card, null,
        React.createElement(CardHeader, null,
          React.createElement("div", { className: "flex items-center justify-between" },
            React.createElement("div", { className: "flex items-center gap-3" },
              React.createElement(CardTitle, { className: "text-base" }, "Results"),
              React.createElement(Badge, { variant: "outline" }, results.length + " places")
            ),
            React.createElement(Button, { variant: "outline", size: "sm", onClick: exportCSV },
              "📥 Export CSV"
            )
          )
        ),
        React.createElement(CardContent, { className: "p-0" },
          React.createElement("div", { className: "overflow-x-auto" },
            React.createElement("table", { className: "w-full text-sm" },
              React.createElement("thead", null,
                React.createElement("tr", { className: "border-b border-border bg-muted/30" },
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium" }, "Name"),
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium w-24" }, "Rating"),
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium w-24" }, "Reviews"),
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium w-32" }, "Category"),
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium w-20" }, "Price"),
                  React.createElement("th", { className: "text-left px-4 py-2 font-medium" }, "Address")
                )
              ),
              React.createElement("tbody", null,
                results.map(function (place, idx) {
                  return React.createElement("tr", {
                    key: idx,
                    className: "border-b border-border/50 hover:bg-muted/20"
                  },
                    React.createElement("td", { className: "px-4 py-2 font-medium" }, place.Name || "-"),
                    React.createElement("td", { className: "px-4 py-2" }, StarRating(place.Rating)),
                    React.createElement("td", { className: "px-4 py-2 text-muted-foreground" }, place.Reviews || "-"),
                    React.createElement("td", { className: "px-4 py-2 text-muted-foreground text-xs" }, place.Category || "-"),
                    React.createElement("td", { className: "px-4 py-2 text-muted-foreground text-xs" }, place.Price_range || "-"),
                    React.createElement("td", { className: "px-4 py-2 text-muted-foreground text-xs max-w-xs truncate" }, place.Address || "-")
                  );
                })
              )
            )
          )
        )
      ),

      // Empty state
      results && results.length === 0 && React.createElement(Card, null,
        React.createElement(CardContent, { className: "flex flex-col items-center justify-center py-12 gap-2" },
          React.createElement("span", { className: "text-muted-foreground" }, "No results found"),
          React.createElement("span", { className: "text-xs text-muted-foreground" }, "Try different query or daerah")
        )
      )

    );
  }

  window.__HERMES_PLUGINS__.register("google-maps-scraper", GMapsScraperPage);
})();
