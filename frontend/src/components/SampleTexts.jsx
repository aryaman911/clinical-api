import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';

const SAMPLE_TEXTS = [
  {
    title: "Protocol Compliance Statement",
    category: "Boilerplate",
    text: `This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by the International Council for Harmonisation (ICH) and in accordance with the ethical principles underlying European Union Directive 2001/20/EC and the United States Code of Federal Regulations, Title 21, Part 50 (21CFR50).

The investigator will ensure that this study is conducted in full conformity with the principles set forth in The Belmont Report: Ethical Principles and Guidelines for the Protection of Human Subjects of Research, as drafted by the US National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research in 1979.

All personnel involved in the conduct of this study have been adequately trained and are qualified by education, training, and experience to perform their respective tasks.`
  },
  {
    title: "Inclusion/Exclusion Criteria",
    category: "Study Section",
    text: `INCLUSION CRITERIA:
1. Age ≥ 18 years at the time of informed consent
2. Histologically or cytologically confirmed diagnosis of advanced solid tumor
3. Eastern Cooperative Oncology Group (ECOG) performance status of 0-1
4. Adequate organ function as defined by laboratory parameters:
   - Absolute neutrophil count ≥ 1,500/μL
   - Platelets ≥ 100,000/μL
   - Hemoglobin ≥ 9.0 g/dL
   - Serum creatinine ≤ 1.5 × upper limit of normal (ULN)
   - Total bilirubin ≤ 1.5 × ULN
5. Willing and able to provide written informed consent

EXCLUSION CRITERIA:
1. Prior treatment with any XYZ kinase inhibitor
2. Known active central nervous system metastases
3. Active autoimmune disease requiring systemic treatment
4. History of interstitial lung disease
5. Pregnant or breastfeeding women`
  },
  {
    title: "Endpoint Definitions",
    category: "Definition",
    text: `PRIMARY ENDPOINT:
Overall Survival (OS) is defined as the time from randomization to death from any cause. Patients who are lost to follow-up or who have not died at the time of analysis will be censored at the date of last known contact.

SECONDARY ENDPOINTS:
Progression-Free Survival (PFS) is defined as the time from randomization to the first documented disease progression according to RECIST v1.1 or death from any cause, whichever occurs first.

Overall Response Rate (ORR) is defined as the proportion of patients who achieve a confirmed complete response (CR) or partial response (PR) according to RECIST v1.1.

Duration of Response (DOR) is defined as the time from the first documented response (CR or PR) to the first documented disease progression or death from any cause.`
  },
  {
    title: "Safety Monitoring Procedures",
    category: "Safety",
    text: `ADVERSE EVENT REPORTING:
Adverse events will be graded according to the National Cancer Institute Common Terminology Criteria for Adverse Events (NCI-CTCAE) version 5.0.

All serious adverse events (SAEs) must be reported to the Sponsor within 24 hours of the investigator becoming aware of the event. SAEs include any adverse event that:
- Results in death
- Is life-threatening
- Requires inpatient hospitalization or prolongation of existing hospitalization
- Results in persistent or significant disability/incapacity
- Is a congenital anomaly/birth defect
- Is an important medical event

An independent Data Safety Monitoring Board (DSMB) will review safety data quarterly and may recommend modifications to the study based on their assessment.`
  },
  {
    title: "Drug Administration",
    category: "Drug Info",
    text: `INVESTIGATIONAL PRODUCT:
ABC-123 is a selective small molecule inhibitor that targets the XYZ kinase pathway. The drug is formulated as 50 mg film-coated tablets for oral administration.

DOSING REGIMEN:
ABC-123 will be administered orally at a dose of 100 mg twice daily (BID), approximately 12 hours apart. Tablets should be taken with food to improve bioavailability.

Treatment will continue until disease progression, unacceptable toxicity, withdrawal of consent, or investigator decision.

DOSE MODIFICATIONS:
For Grade 3 or 4 adverse events related to ABC-123, dosing should be interrupted until recovery to Grade ≤ 1, then resumed at a reduced dose level:
- First dose reduction: 75 mg BID
- Second dose reduction: 50 mg BID
- Discontinue if unable to tolerate 50 mg BID`
  }
];

function SampleTexts({ onSelect }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4 text-gray-500" />
          <span className="font-semibold text-gray-900">Sample Clinical Texts</span>
          <span className="text-sm text-gray-500">({SAMPLE_TEXTS.length} examples)</span>
        </div>
        {expanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="p-4 space-y-3 max-h-64 overflow-y-auto">
          {SAMPLE_TEXTS.map((sample, index) => (
            <button
              key={index}
              onClick={() => {
                onSelect(sample.text);
                setExpanded(false);
              }}
              className="w-full text-left p-3 border border-gray-200 rounded-lg hover:border-clinical-300 hover:bg-clinical-50 transition-all group"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900 group-hover:text-clinical-700">
                  {sample.title}
                </span>
                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                  {sample.category}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                {sample.text.substring(0, 150)}...
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default SampleTexts;
