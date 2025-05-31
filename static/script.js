function uploadFiles() {
    let aadhaarFile = document.getElementById("aadhaarInput").files[0];
    let smartcardFile = document.getElementById("smartcardInput").files[0];

    if (!aadhaarFile || !smartcardFile) {
        alert("Please select both Aadhaar and Smart Card images.");
        console.log("❌ Missing files: Aadhaar =", aadhaarFile, "Smart Card =", smartcardFile);
        return;
    }

    let formData = new FormData();
    formData.append("aadhaar_image", aadhaarFile);
    formData.append("smartcard_image", smartcardFile);

    let progressBar = document.getElementById("progress-bar");
    let progressContainer = document.getElementById("progress-container");

    progressContainer.style.display = "block"; // Show progress bar

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    /*.then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("result").innerText = "Error: " + data.error;
        } else {
            document.getElementById("result").innerHTML = 
                `<b>Aadhar:</b> ${data.aadhar} <br> 
                 <b>Smart Card:</b> ${data.smartcard} <br> 
                 <b>Verified:</b> ${data.verified ? "✔️ Yes" : "❌ No"}`;
        }
    })
    .then(response => response.text())
    .then(html => {
        document.body.innerHTML = html; 
    })
    .catch(error => console.error("Error:", error));
} */
    
    .then(response => {
        let progress = 0;
        let interval = setInterval(() => {
            if (progress >= 90) clearInterval(interval);
            progress += 20;
            progressBar.style.width = progress + "%";
        }, 300);

        return response.text();
    })
    
    .then(html => {
    progressBar.style.width = "100%";
    setTimeout(() => {
        document.body.innerHTML = html;

        // ✅ Rebind event listener for the new DOM
        initsendReportBtn();
    }, 500);
})
    
    .catch(error => console.error("Error:", error));
}

function initsendReportBtn(){
const sendReportBtn=
    document.getElementById("sendReportBtn");
if (sendReportBtn) {
     sendReportBtn.addEventListener("click", function (){
    console.log("Send report button clicked");
    const aadharNumber=sendReportBtn.dataset.aadhar;
    const smartCardNumber= sendReportBtn.dataset.smartcard;
    console.log(aadharNumber, smartCardNumber);
         fetch("/send_report", 
        { method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ aadhar_number: aadharNumber, 
        smart_card_number: smartCardNumber }) }) 
        .then(response => response.json()) 
        .then(data => { 
            alert(data.message);})
            .catch(error=> {
                console.error('error sending report:', error);
                alert("failed to send verification report.");
            });
        });
    }else{
        console.warn("sendReportbtn not found in the dom");
    }
            }
            
function checkEligibility() {
    let name = document.getElementById("name").value;
    let category = document.getElementById("category").value;
    let caste = document.getElementById("caste").value;
    let income = parseInt(document.getElementById("income").value);
    let loanType = document.getElementById("loanType").value;
    
    let eligibleSchemes = [];

    // Eligibility criteria
    if (category === "student" && income <= 200000 && loanType === "school") {
        eligibleSchemes.push("PM-Vidyalaxmi Scheme");
    }
    if (category === "business" && caste === "sc" || caste === "st") {
        eligibleSchemes.push("Stand-Up India Scheme");
    }
    if (category === "farmer" && income <= 200000) {
        eligibleSchemes.push("Kisan Credit Card (KCC)");
    }
    if (category === "business" && income <= 200000) {
        eligibleSchemes.push("Pradhan Mantri Mudra Yojana (PMMY)");
    }

    // Display result
    let resultDiv = document.getElementById("result");
    if (eligibleSchemes.length > 0) {
        resultDiv.innerHTML = `<p>${name}, you are eligible for:</p> <ul>${eligibleSchemes.map(scheme => `<li>${scheme}</li>`).join("")}</ul>`;
    } else {
        resultDiv.innerHTML = `<p>Sorry, ${name}, you are not eligible for any loan waiver schemes.</p>`;
    }
}


document.addEventListener("DOMContentLoaded", function () {
    let hash = window.location.hash;
    if (hash) {
        let target = document.querySelector(hash);
        if (target) {
            window.scrollTo({ top: target.offsetTop - 50, behavior: "smooth" });
        }
    }
    initsendReportBtn();
    iinitsendReportBtn();
});
// Save comments locally (can be connected to backend later)
//send report for failed verification
function iinitsendReportBtn(){
const sendReportBtnForFail=
    document.getElementById("sendReportBtnForFail");
if (sendReportBtnForFail) {
     sendReportBtnForFail.addEventListener("click", function (){
    console.log("Send report button clicked");
    const aadharNumber=sendReportBtnForFail.dataset.aadhar;
    const smartCardNumber= sendReportBtnForFail.dataset.smartcard;
    console.log(aadharNumber, smartCardNumber);
         fetch("/send_report_failure", 
        {   method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ aadhar_number: aadharNumber, 
        smart_card_number: smartCardNumber }) }) 
        .then(response => response.json()) 
        .then(data => { 
            alert(data.message);})
            .catch(error=> {
                console.error('error sending report:', error);
                alert("failed to send verification report.");
            });
        });
    }else{
        console.warn("sendReportbtnForFail not found in the dom");
    }
            }
            