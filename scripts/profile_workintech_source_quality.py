#!/usr/bin/env python3
"""Reproducible local read-only football source-quality profile.

No cloud access, no mutation, no credentials, no screenshot capture.
The metrics characterize a historic Kaggle archive; they cannot establish a
live match feed or independently validate a Power BI runtime refresh.
"""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(r"C:\ProgramData\SentinelX\workspace\football-recovery-20261027")
def build_profile(archive: Path, manifest: Path):
    try:
        import duckdb
    except ModuleNotFoundError:
        # The authorized offline recovery bundle vendors DuckDB for Windows;
        # do not install packages, reach the network or invoke cloud credentials.
        sys.path.insert(0,str(ROOT/'python_libs'))
        import duckdb
    files={}
    for name in ("games","appearances","players","player_valuations","transfers","clubs","competitions"):
        f=archive/(name+".parquet")
        if not f.is_file():
            raise FileNotFoundError(f"Required source Parquet not found: {f}")
        files[name]=f.as_posix()
    original=json.loads(manifest.read_text("utf-8-sig"))
    conn=duckdb.connect(":memory:")
    conn.execute("SET memory_limit='1GB'")
    for name,f in files.items():
        # CREATE VIEW does not support prepared placeholders in DuckDB.
        # Only fixed allowlisted table names and local prevalidated paths enter SQL.
        safe_path=f.replace("'","''")
        conn.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{safe_path}')")
    def one(sql):
        row=conn.execute(sql).fetchone()
        return tuple(int(x) if isinstance(x,int) else x for x in row)
    source_counts={}
    for n in files:
        count=one(f"SELECT COUNT(*) FROM {n}")[0]
        expected=int(original["tables"][n]["source_rows"])
        source_counts[n]={"actual":count,"expected":expected,"match":count==expected}
    games=one("""
      SELECT COUNT(*), COUNT(DISTINCT game_id),
             MIN(date), MAX(date),
             COUNT(*) FILTER(WHERE date IS NULL),
             COUNT(*) FILTER(WHERE home_club_goals<0 OR away_club_goals<0),
             COUNT(*) FILTER(WHERE home_club_id=away_club_id AND home_club_id IS NOT NULL)
      FROM games""")
    valuations=one("""
      WITH grouped AS (
        SELECT player_id, date, COUNT(*) AS row_count,
               COUNT(DISTINCT market_value_in_eur) AS distinct_values
        FROM player_valuations
        GROUP BY player_id,date
      )
      SELECT COUNT(*) FILTER(WHERE row_count>1),
             COALESCE(SUM(row_count-1) FILTER(WHERE row_count>1),0),
             COUNT(*) FILTER(WHERE distinct_values>1)
      FROM grouped
    """)
    valuation_dates=one("""
      SELECT MIN(date),MAX(date),
        COUNT(*) FILTER(WHERE date IS NULL),
        COUNT(*) FILTER(WHERE market_value_in_eur<=0),
        COUNT(*) FILTER(WHERE market_value_in_eur IS NULL)
      FROM player_valuations
    """)
    game_links=one("""
      SELECT COUNT(*) FILTER(WHERE NOT EXISTS
       (SELECT 1 FROM games g WHERE g.game_id=a.game_id)),
       COUNT(*) FILTER(WHERE NOT EXISTS
       (SELECT 1 FROM players p WHERE p.player_id=a.player_id))
      FROM appearances a
    """)
    unknown_competitions=conn.execute("""
      SELECT g.competition_id,COUNT(*) AS matches
      FROM games g LEFT JOIN competitions c ON g.competition_id=c.competition_id
      WHERE c.competition_id IS NULL
      GROUP BY g.competition_id ORDER BY matches DESC
    """).fetchall()
    transfers=one("""
      SELECT MIN(transfer_date),MAX(transfer_date),
             COUNT(*) FILTER(WHERE transfer_date IS NULL),
             COUNT(*) FILTER(WHERE transfer_fee<0),
             COUNT(*) FILTER(WHERE market_value_in_eur<0)
      FROM transfers
    """)
    issue_list=[]
    def issue(code,severity,count,impact):
        if count:
            issue_list.append({"code":code,"severity":severity,"affected":int(count),"impact":impact})
    issue("SOURCE_ROW_COUNT_MISMATCH","critical",
          sum(1 for x in source_counts.values() if not x["match"]),"Rows differ from the previously loaded archive.")
    issue("DUPLICATE_GAME_ID","critical",
          games[0]-games[1],"Matches may be double-counted by business intelligence.")
    issue("MISSING_APPEARANCE_GAME","high",
          game_links[0],"Appearance-to-game joins lose or misattribute records.")
    issue("MISSING_APPEARANCE_PLAYER","high",
          game_links[1],"Appearance-to-player joins lose or misattribute records.")
    issue("CONFLICTING_SAME_DAY_VALUATIONS","high",
          valuations[2],"ML supervised targets require deterministic exclusion; never select arbitrary target.")
    issue("UNMAPPED_COMPETITION_CODES_IN_SOURCE","medium",
          sum(int(n) for _,n in unknown_competitions),
          "Historic source lacks competition descriptions; staging uses explicit unknown members, not invented metadata.")
    future_transfers=one("SELECT COUNT(*) FROM transfers WHERE transfer_date > DATE '2026-10-27'")[0]
    issue("FUTURE_DATED_SOURCE_TRANSFERS","medium",future_transfers,
          "Future effective transfer dates may represent planned moves. Outcome marts must exclude them until observed.")
    issue("NONPOSITIVE_SOURCE_VALUATIONS","medium",valuation_dates[3],
          "Nonpositive valuation cannot supply a positive supervised ML target.")
    issue("MISSING_GAME_DATE","high",games[4],"Match-series temporal logic may be incomplete.")
    issue("INVALID_SCORES","high",games[5],"Goals must be nonnegative when populated.")
    issue("SAME_HOME_AND_AWAY_CLUB","high",games[6],"Potential invalid match identifiers.")
    return {
       "generated_utc":datetime.now(timezone.utc).isoformat(),
       "scope":"historical Kaggle Parquet archive only, not live BigQuery or Power BI",
       "manifest_archive_sha256":original.get("source_archive_sha256"),
       "rows":source_counts,
       "matches":{"rows":games[0],"unique_game_ids":games[1],
                  "min_date":str(games[2]),"max_date":str(games[3]),
                  "null_dates":games[4],"negative_score_rows":games[5],
                  "same_home_away_club_rows":games[6]},
       "valuations":{"rows":source_counts["player_valuations"]["actual"],
                     "same_player_date_groups_with_duplicates":valuations[0],
                     "extra_duplicate_rows":valuations[1],
                     "groups_with_conflicting_positive_values":valuations[2],
                     "min_date":str(valuation_dates[0]),"max_date":str(valuation_dates[1]),
                     "null_dates":valuation_dates[2],
                     "nonpositive_values":valuation_dates[3],
                     "null_values":valuation_dates[4]},
       "appearance_orphans":{"missing_games":game_links[0],"missing_players":game_links[1]},
       "source_competitions_without_dictionary_entry":[
          {"code":str(code),"games":int(n)} for code,n in unknown_competitions],
       "transfers":{"min_date":str(transfers[0]),"max_date":str(transfers[1]),
                    "missing_date_rows":transfers[2],
                    "negative_fee_rows":transfers[3],
                    "negative_value_rows":transfers[4],
                    "future_dated_as_of_2026_10_27":future_transfers},
       "issues":issue_list,
       "status":"DATA_SOURCE_RISK_REVIEW" if issue_list else "SOURCE_PROFILE_PASS",
       "provenance_caveat":"Historical source facts; not a proof of live October 27 football completeness.",
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,default=ROOT/"kaggle_archive_typed_parquet")
    parser.add_argument("--manifest",type=Path,default=ROOT/"kaggle_archive_typed_manifest.json")
    parser.add_argument("--report",type=Path,default=ROOT/"workintech_source_quality_20261027.json")
    args=parser.parse_args()
    try:
        profile=build_profile(args.archive,args.manifest)
    except (OSError,ValueError,RuntimeError,KeyError) as error:
        raise SystemExit("SOURCE_PROFILE_STOPPED: "+type(error).__name__+": "+str(error))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(profile,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"status":profile["status"],
          "max_game_date":profile["matches"]["max_date"],
          "conflicting_valuations":profile["valuations"]["groups_with_conflicting_positive_values"],
          "missing_appearance_games":profile["appearance_orphans"]["missing_games"],
          "issue_count":len(profile["issues"]),
          "report":str(args.report)},ensure_ascii=False))
if __name__=="__main__":main()
