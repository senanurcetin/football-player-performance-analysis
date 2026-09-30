param(
    [Parameter(Mandatory = $false)]
    [int]$Port = 0
)

if ($Port -eq 0) {
    $proc = Get-Process msmdsrv -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $proc) { throw "Power BI Desktop açık değil veya msmdsrv bulunamadı." }
    $portLine = netstat -ano | Select-String "LISTENING" | Select-String "\s$($proc.Id)$" | Select-Object -First 1
    if ($null -eq $portLine) { throw "msmdsrv portu tespit edilemedi (PID $($proc.Id))." }
    $Port = [int]($portLine.Line.Trim() -split '\s+')[1].Split(':')[-1]
    Write-Output "msmdsrv otomatik tespit edildi: PID $($proc.Id) → Port $Port"
}

$tum  = 'T' + [char]0x00FC + 'm'          # Tüm
$ulke = [char]0x00FC + 'lkeler'            # ülkeler
$Ulke = [char]0x00DC + 'lkeler'            # Ülkeler (capital)

$bin = 'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.155.756.0_x64__8wekyb3d8bbwe\bin'
Add-Type -Path (Join-Path $bin 'Microsoft.AnalysisServices.Server.Core.dll')
Add-Type -Path (Join-Path $bin 'Microsoft.AnalysisServices.Server.Tabular.dll')

$measures = @(
    # --- Page 005 (Transfer ve Piyasa Değeri Analizi) Measures ---
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Transfer Count'
        Expression = 'DISTINCTCOUNT(fct_transfer_market_value_analysis[transfer_key])'
        Format = '#,0 "transfer"'
        Folder = 'Market Value Analysis\01 Scope'
        Description = 'Distinct transfer records in the active filter context.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Known Fee Transfer Count'
        Expression = 'CALCULATE([Transfer Count], fct_transfer_market_value_analysis[has_known_transfer_fee] = TRUE())'
        Format = '#,0 "transfer"'
        Folder = 'Market Value Analysis\01 Scope'
        Description = 'Transfers with a known transfer fee.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Known Fee Coverage %'
        Expression = 'COALESCE(DIVIDE([Known Fee Transfer Count], [Transfer Count]), 0)'
        Format = '0.0%'
        Folder = 'Market Value Analysis\02 Data Trust'
        Description = 'Share of transfer records with a known transfer fee.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Average Known Transfer Fee'
        Expression = 'CALCULATE(AVERAGE(fct_transfer_market_value_analysis[transfer_fee]), fct_transfer_market_value_analysis[has_known_transfer_fee] = TRUE())'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Average transfer fee, excluding unknown fee records.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Total Known Transfer Fee'
        Expression = 'CALCULATE(SUM(fct_transfer_market_value_analysis[transfer_fee]), fct_transfer_market_value_analysis[has_known_transfer_fee] = TRUE())'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Total known transfer fee in the active filter context.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Comparable Transfer Count'
        Expression = 'CALCULATE([Transfer Count], fct_transfer_market_value_analysis[has_fee_market_value_comparison] = TRUE())'
        Format = '#,0 "transfer"'
        Folder = 'Market Value Analysis\02 Data Trust'
        Description = 'Transfers with both a known fee and a market-value baseline.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Comparison Coverage %'
        Expression = 'DIVIDE([Comparable Transfer Count], [Transfer Count])'
        Format = '0.0%'
        Folder = 'Market Value Analysis\02 Data Trust'
        Description = 'Share of transfer records eligible for fee versus market-value comparison.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Average Fee Premium Discount %'
        Expression = 'DIVIDE(CALCULATE(AVERAGE(fct_transfer_market_value_analysis[fee_market_value_difference_pct]), fct_transfer_market_value_analysis[has_fee_market_value_comparison] = TRUE()), 100)'
        Format = '0.0%'
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Average fee premium or discount versus the market-value baseline.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Post Transfer Outcome Count'
        Expression = 'CALCULATE([Transfer Count], fct_transfer_market_value_analysis[has_post_transfer_value_change] = TRUE())'
        Format = '#,0 "transfer"'
        Folder = 'Market Value Analysis\02 Data Trust'
        Description = 'Transfers with an observable post-transfer market-value outcome.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Post Transfer Outcome Coverage %'
        Expression = 'COALESCE(DIVIDE([Post Transfer Outcome Count], [Transfer Count]), 0)'
        Format = '0.0%'
        Folder = 'Market Value Analysis\02 Data Trust'
        Description = 'Share of transfers with an observable post-transfer value outcome.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Average Post Transfer Value Change %'
        Expression = 'DIVIDE(CALCULATE(AVERAGE(fct_transfer_market_value_analysis[market_value_change_after_transfer_pct]), fct_transfer_market_value_analysis[has_post_transfer_value_change] = TRUE()), 100)'
        Format = '0.0%'
        Folder = 'Market Value Analysis\04 Outcomes'
        Description = 'Average post-transfer market-value change for observable outcomes.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Value Increase Rate %'
        Expression = 'COALESCE(DIVIDE(CALCULATE([Transfer Count], fct_transfer_market_value_analysis[market_value_direction_after_transfer] = "increase"), [Post Transfer Outcome Count]), 0)'
        Format = '0.0%'
        Folder = 'Market Value Analysis\04 Outcomes'
        Description = 'Share of observable transfer outcomes with a market-value increase.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Selected Transfer Player'
        Expression = 'SELECTEDVALUE(fct_transfer_market_value_analysis[player_name], "Oyuncu secilmedi")'
        Format = ''
        Folder = 'Market Value Analysis\05 Dynamic Context'
        Description = 'Selected player label for drill-through pages.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Transfer Context Summary'
        Expression = 'VAR SeasonLabel = SELECTEDVALUE(fct_transfer_market_value_analysis[transfer_season], "' + $tum + ' sezonlar") VAR PositionLabel = SELECTEDVALUE(fct_transfer_market_value_analysis[position], "' + $tum + ' pozisyonlar") RETURN SeasonLabel & " | " & PositionLabel & " | " & FORMAT([Transfer Count], "#,0") & " transfer"'
        Format = ''
        Folder = 'Market Value Analysis\05 Dynamic Context'
        Description = 'Dynamic context summary driven by active filters.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Page 005 Dynamic Title'
        Expression = ('VAR s = SELECTEDVALUE(fct_transfer_market_value_analysis[transfer_season], "' + $tum + ' Sezonlar") ' +
                      'VAR p = SELECTEDVALUE(fct_transfer_market_value_analysis[pozisyon_tr], "' + $tum + ' Pozisyonlar") ' +
                      'RETURN "' + [char]::ConvertFromUtf32(0x1F4B0) +
                      ' Transfer & Piyasa De' + [char]0x011F + 'eri  ' + [char]0x2502 +
                      '  " & s & "  ' + [char]0x2502 + '  " & p')
        Format = ''
        Folder = 'Market Value Analysis\05 Dynamic Context'
        Description = 'Dynamic page title driven by active slicer selections.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'High Premium Transfer Count'
        Expression = 'CALCULATE([Transfer Count], fct_transfer_market_value_analysis[fee_market_value_difference_pct] > 30)'
        Format = '#,0 "transfer"'
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Transfers where the fee exceeds market value by more than 30 percent — competitive bidding signal.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Transfer Value Index'
        Expression = 'DIVIDE(CALCULATE(SUM(fct_transfer_market_value_analysis[transfer_fee]), fct_transfer_market_value_analysis[has_known_transfer_fee] = TRUE()), CALCULATE(SUM(fct_transfer_market_value_analysis[market_value_baseline]), fct_transfer_market_value_analysis[has_market_value_baseline] = TRUE()))'
        Format = '0.00x'
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Ratio of total known fees to total market value baselines — market efficiency index.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'YoY Avg Fee Change %'
        Expression = ('VAR CY = CALCULATE([Average Known Transfer Fee]) ' +
                      'VAR PY = CALCULATE([Average Known Transfer Fee], FILTER(ALL(fct_transfer_market_value_analysis[transfer_year]), fct_transfer_market_value_analysis[transfer_year] = MAX(fct_transfer_market_value_analysis[transfer_year]) - 1)) ' +
                      'RETURN DIVIDE(CY - PY, PY)')
        Format = '+0.0%;-0.0%;0.0%'
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Year-over-year change in average known transfer fee.'
    },
    @{
        Table = 'fct_transfer_market_value_analysis'
        Name = 'Max Known Transfer Fee'
        Expression = 'CALCULATE(MAX(fct_transfer_market_value_analysis[transfer_fee]), fct_transfer_market_value_analysis[has_known_transfer_fee] = TRUE())'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Analysis\03 Commercial Value'
        Description = 'Maximum known transfer fee in the active filter context.'
    },

    # --- Page 006 (Oyuncu Piyasa Değeri Tahmini) Measures ---
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Scored Player Count'
        Expression = 'DISTINCTCOUNT(ml_player_market_value_current_predictions[player_id])'
        Format = '#,0 "oyuncu"'
        Folder = 'Market Value Prediction\01 Scope'
        Description = 'Distinct players with a current market-value prediction.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Decision Ready Player Count'
        Expression = 'CALCULATE([Scored Player Count], ml_player_market_value_current_predictions[prediction_quality_status] IN {"high", "medium"})'
        Format = '#,0 "oyuncu"'
        Folder = 'Market Value Prediction\02 Trust'
        Description = 'Players with high or medium prediction quality.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Decision Ready Rate %'
        Expression = 'COALESCE(DIVIDE([Decision Ready Player Count], [Scored Player Count]), 0)'
        Format = '0.0%'
        Folder = 'Market Value Prediction\02 Trust'
        Description = 'Share of scored players suitable for decision support.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Predicted Market Value'
        Expression = 'AVERAGE(ml_player_market_value_current_predictions[predicted_market_value_eur])'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Prediction\03 Valuation'
        Description = 'Average current predicted market value.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Previous Market Value'
        Expression = 'AVERAGE(ml_player_market_value_current_predictions[previous_market_value_eur])'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Prediction\03 Valuation'
        Description = 'Average previous observed market value.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Prediction Upside %'
        Expression = 'DIVIDE(AVERAGE(ml_player_market_value_current_predictions[prediction_delta_vs_previous_pct]), 100)'
        Format = '0.0%'
        Folder = 'Market Value Prediction\04 Opportunity'
        Description = 'Average predicted percentage change versus previous market value.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Positive Upside Player Count'
        Expression = 'CALCULATE([Scored Player Count], ml_player_market_value_current_predictions[prediction_delta_vs_previous_pct] > 0)'
        Format = '#,0 "oyuncu"'
        Folder = 'Market Value Prediction\04 Opportunity'
        Description = 'Players with positive predicted upside versus previous market value.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Positive Upside Rate %'
        Expression = 'COALESCE(DIVIDE([Positive Upside Player Count], [Scored Player Count]), 0)'
        Format = '0.0%'
        Folder = 'Market Value Prediction\04 Opportunity'
        Description = 'Share of scored players with positive predicted upside.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Prediction Interval'
        Expression = 'AVERAGE(ml_player_market_value_current_predictions[prediction_interval_eur])'
        Format = ([char]0x20AC + '0.0')
        Folder = 'Market Value Prediction\02 Trust'
        Description = 'Average prediction interval width.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Relative Prediction Interval %'
        Expression = 'DIVIDE([Average Prediction Interval], [Average Predicted Market Value])'
        Format = '0.0%'
        Folder = 'Market Value Prediction\02 Trust'
        Description = 'Average prediction interval relative to predicted market value.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Selected Prediction Player'
        Expression = 'SELECTEDVALUE(ml_player_market_value_current_predictions[player_name], "Oyuncu secilmedi")'
        Format = ''
        Folder = 'Market Value Prediction\05 Dynamic Context'
        Description = 'Selected player label for drill-through pages.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Prediction Context Summary'
        Expression = 'VAR PositionLabel = SELECTEDVALUE(ml_player_market_value_current_predictions[position], "' + $tum + ' pozisyonlar") VAR CountryLabel = SELECTEDVALUE(ml_player_market_value_current_predictions[competition_country_name], "' + $tum + ' ' + $ulke + '") RETURN PositionLabel & " | " & CountryLabel & " | " & FORMAT([Scored Player Count], "#,0") & " oyuncu"'
        Format = ''
        Folder = 'Market Value Prediction\05 Dynamic Context'
        Description = 'Dynamic prediction context summary driven by active filters.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'ML Page Dynamic Title'
        Expression = ('VAR p = SELECTEDVALUE(ml_player_market_value_current_predictions[pozisyon_tr], "' + $tum + ' Pozisyonlar") ' +
                      'VAR c = SELECTEDVALUE(ml_player_market_value_current_predictions[competition_country_name], "' + $tum + ' ' + $Ulke + '") ' +
                      'RETURN "' + [char]0x2B50 +
                      ' Piyasa De' + [char]0x011F + 'eri Tahmini  ' + [char]0x2502 +
                      '  " & p & "  ' + [char]0x2502 + '  " & c')
        Format = ''
        Folder = 'Market Value Prediction\05 Dynamic Context'
        Description = 'Dynamic page title driven by active slicer selections.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = ('B' + [char]0x00FC + 'y' + [char]0x00FC + 'k Art' + [char]0x0131 + [char]0x015F + ' Oyuncu Count')
        Expression = 'CALCULATE([Scored Player Count], ml_player_market_value_current_predictions[prediction_delta_vs_previous_pct] > 20)'
        Format = '#,0 "oyuncu"'
        Folder = 'Market Value Prediction\04 Opportunity'
        Description = 'Players with predicted upside greater than 20 percent — high-opportunity targets.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'Average Prediction Confidence %'
        Expression = '1 - [Average Relative Prediction Interval %]'
        Format = '0.0%'
        Folder = 'Market Value Prediction\02 Trust'
        Description = 'Inverse of average relative interval — higher means more confident predictions.'
    },
    @{
        Table = 'ml_player_market_value_current_predictions'
        Name = 'High Upside Decision Ready Count'
        Expression = 'CALCULATE([Decision Ready Player Count], ml_player_market_value_current_predictions[prediction_delta_vs_previous_pct] > 0)'
        Format = '#,0 "oyuncu"'
        Folder = 'Market Value Prediction\04 Opportunity'
        Description = 'Decision-ready players with positive predicted upside — actionable long list.'
    },

    # --- Quality Gates ---
    @{
        Table = 'ml_player_market_value_quality_gates'
        Name = 'Quality Gates Passed'
        Expression = 'CALCULATE(COUNTROWS(ml_player_market_value_quality_gates), ml_player_market_value_quality_gates[passed] = TRUE())'
        Format = '#,0'
        Folder = 'ML Model Quality\01 Gates'
        Description = 'Number of quality gates that passed.'
    },
    @{
        Table = 'ml_player_market_value_quality_gates'
        Name = 'Quality Gates Total'
        Expression = 'COUNTROWS(ml_player_market_value_quality_gates)'
        Format = '#,0'
        Folder = 'ML Model Quality\01 Gates'
        Description = 'Total number of quality gates evaluated.'
    }
)

$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$Port")

try {
    $database = $server.Databases[0]
    $model = $database.Model

    # Add/update measures only
    foreach ($definition in $measures) {
        $table = $model.Tables.Find($definition.Table)
        if ($null -eq $table) {
            throw "Table not found: $($definition.Table)"
        }

        $measure = $table.Measures.Find($definition.Name)
        if ($null -eq $measure) {
            $measure = New-Object Microsoft.AnalysisServices.Tabular.Measure
            $measure.Name = $definition.Name
            $table.Measures.Add($measure)
            Write-Output "Added measure: $($definition.Table)[$($definition.Name)]"
        } else {
            Write-Output "Updated measure: $($definition.Table)[$($definition.Name)]"
        }

        $measure.Expression = $definition.Expression
        $measure.FormatString = $definition.Format
        $measure.DisplayFolder = $definition.Folder
        $measure.Description = $definition.Description
    }

    $model.SaveChanges()
    Write-Output "Successfully injected and saved all measures!"
}
finally {
    $server.Disconnect()
}
