export type ForecastDetail = {
  version:number; generated_at:string; as_of:string;
  kind:'binary'|'multiple_choice'|'numeric'|'discrete'; unit:string|null;
  rows:{label:string;value:number}[];
};
export type QuestionDetail = {
  title?:string; group_title?:string|null;
  question_details?:{background:string|null;resolution_criteria:string|null;fine_print:string|null};
  forecast?:ForecastDetail;
  community?:{status:'unavailable';observed_at:null;reason:string};
};
const probability = new Intl.NumberFormat('en-CA',{style:'percent',maximumFractionDigits:2});
const number = new Intl.NumberFormat('en-CA',{maximumSignificantDigits:7});

export function ForecastComparison({record,date}:{record:QuestionDetail;date:(value:string)=>string}) {
  const forecast=record.forecast;
  const details=record.question_details;
  return <div className="forecast-comparison">
    {forecast ? <>
      <p className="forecast-caption">Bot forecast · version {forecast.version} · generated {date(forecast.generated_at)}</p>
      <p>Forecast as of {date(forecast.as_of)} · Recorded prediction; submission status is shown separately.</p>
      <table>
        <caption>{forecast.kind==='numeric'||forecast.kind==='discrete'?`Recorded percentiles${forecast.unit?` · ${forecast.unit}`:''}`:'Recorded probabilities'}</caption>
        <thead><tr><th scope="col">{forecast.kind==='numeric'||forecast.kind==='discrete'?'Percentile':'Outcome'}</th><th scope="col">Bot</th><th scope="col">Community</th></tr></thead>
        <tbody>{forecast.rows.map(row=><tr key={row.label}><th scope="row">{row.label}</th><td>{forecast.kind==='binary'||forecast.kind==='multiple_choice'?probability.format(row.value):number.format(row.value)}</td><td><span aria-label="Community forecast unavailable">—</span></td></tr>)}</tbody>
      </table>
    </> : <p>Recorded bot forecast unavailable in this observation.</p>}
    <p className="community-note"><strong>Community unavailable.</strong> {record.community?.reason||'No community prediction has been imported.'}</p>
    {details&&(details.background||details.resolution_criteria||details.fine_print)&&<details>
      <summary>Question details at forecast time</summary>
      {details.background&&<><h4>Background</h4><p>{details.background}</p></>}
      {details.resolution_criteria&&<><h4>Resolution criteria</h4><p>{details.resolution_criteria}</p></>}
      {details.fine_print&&<><h4>Fine print</h4><p>{details.fine_print}</p></>}
    </details>}
  </div>;
}
