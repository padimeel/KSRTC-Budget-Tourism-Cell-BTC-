<script>
document.addEventListener("DOMContentLoaded", () => {
  const packageId = 1; // <-- CHANGE THIS ID
  const url = `http://127.0.0.1:8000/api/packages/${packageId}/`;

  axios.get(url)
    .then(response => {
      const itineraries = response.data.itineraries;
      const container = document.getElementById("itinerary-container");

      container.innerHTML = ""; // clear old items

      itineraries.forEach(item => {
        container.innerHTML += `
          <div class="border border-gray-200 rounded-md p-5 relative">
            <div
              class="absolute -top-4 -left-4 flex items-center justify-center w-11 h-11 bg-[#E11D48] text-white font-bold rounded-full"
            >
              ${item.day_number}
            </div>

            <div class="ml-2">
              <h5 class="font-bold text-lg mt-2">${item.title}</h5>
              <p>${item.description}</p>
              <p class="text-gray-500 mb-0">
                ${item.additional_note || ""}
              </p>
            </div>
          </div>
        `;
      });
    })
    .catch(err => {
      console.error("Error loading itinerary:", err);
    });
});
</script>




