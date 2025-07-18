import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';

const PostReview = () => {
  const [dealer, setDealer] = useState({});
  const [review, setReview] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [date, setDate] = useState("");
  const [carmodels, setCarmodels] = useState([]);
  const [modelError, setModelError] = useState("");

  let curr_url = window.location.href;
  let root_url = curr_url.substring(0, curr_url.indexOf("postreview"));
  let params = useParams();
  let id = params.id;
  let dealer_url = root_url + `djangoapp/dealer/${id}`;
  let review_url = root_url + `djangoapp/add_review`;
  let carmodels_url = root_url + `djangoapp/get_cars`;

  const postreview = async () => {
    let name = sessionStorage.getItem("firstname") + " " + sessionStorage.getItem("lastname");
    if (name.includes("null")) {
      name = sessionStorage.getItem("username");
    }

    // Validation check
    if (!model || review === "" || date === "" || year === "") {
      if (!model) {
        setModelError("Please select a car make and model.");
      } else {
        setModelError(""); // Clear if already selected
      }
      alert("All details are mandatory");
      return;
    }

    setModelError(""); // Clear error when all fields are valid

    let model_split = model.split(" ");
    let make_chosen = model_split[0];
    let model_chosen = model_split[1];

    let jsoninput = JSON.stringify({
      "name": name,
      "dealership": id,
      "review": review,
      "purchase": true,
      "purchase_date": date,
      "car_make": make_chosen,
      "car_model": model_chosen,
      "car_year": year,
    });

    console.log(jsoninput);

    const res = await fetch(review_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", 
      body: jsoninput,
    });

    if (res.status === 200) {
    window.location.href = window.location.origin + "/dealer/" + id;
} else {
    const json = await res.json();
    console.error("Failed to post review:", json);
    alert("Something went wrong while posting your review.");
}


  };

  const get_dealer = async () => {
    const res = await fetch(dealer_url, {
      method: "GET"
    });
    const retobj = await res.json();

    if (retobj.status === 200) {
      let dealerobjs = Array.from(retobj.dealer);
      if (dealerobjs.length > 0)
        setDealer(dealerobjs[0]);
    }
  };

  const get_cars = async () => {
    const res = await fetch(carmodels_url, {
      method: "GET"
    });
    const retobj = await res.json();

    let carmodelsarr = Array.from(retobj.CarModels);
    setCarmodels(carmodelsarr);
  };

  useEffect(() => {
    get_dealer();
    get_cars();
  }, []);

  return (
    <div>
      <Header />
      <div style={{ margin: "5%" }}>
        <h1 style={{ color: "darkblue" }}>{dealer.full_name}</h1>

        <textarea
          id='review'
          cols='50'
          rows='7'
          placeholder='Write your review here...'
          onChange={(e) => setReview(e.target.value)}
        ></textarea>

        <div className='input_field'>
          Purchase Date
          <input type="date" onChange={(e) => setDate(e.target.value)} />
        </div>

        <div className='input_field'>
          Car Make
          <select
            name="cars"
            id="cars"
            value={model || ""}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="" disabled hidden>Choose Car Make and Model</option>
            {carmodels.map(carmodel => (
              <option
                key={carmodel.CarMake + carmodel.CarModel}
                value={carmodel.CarMake + " " + carmodel.CarModel}
              >
                {carmodel.CarMake} {carmodel.CarModel}
              </option>
            ))}
          </select>
          {modelError && <div style={{ color: "red", marginTop: "5px" }}>{modelError}</div>}
        </div>

        <div className='input_field'>
          Car Year
          <input
            type="number"
            onChange={(e) => setYear(e.target.value)}
            max={2023}
            min={2015}
          />
        </div>

        <div>
          <button className='postreview' onClick={postreview}>Post Review</button>
        </div>
      </div>
    </div>
  );
};

export default PostReview;
