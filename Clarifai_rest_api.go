package main

import "fmt"
import "log"
import "net/http"
import "io/ioutil"
import "strings"
import "bytes"
import "encoding/json"
import "sort"

var println = fmt.Println
var printf = fmt.Print
var scanln = fmt.Scanln
var scanf = fmt.Scanf

var API_KEY string = "Key ff507c986e8d457cbe25d4d0e2525ed6";
var CLARIFAI_PREDICT_API_URL string = "https://api.clarifai.com/v2/models/aaa03c23b3724a16a56b629203edc62c/outputs";
var IMAGES_URL = "https://s3.amazonaws.com/clarifai-data/backend/api-take-home/images.txt";

var imageIdAndImageMap map[string]string

type ImagePredictDetails struct {
	image string
	value float32
}

var tagAndImagePredictDetails map[string][]ImagePredictDetails

// Main function
func main() {

	var option int

	imageIdAndImageMap = make(map[string]string)
	tagAndImagePredictDetails = make(map[string][]ImagePredictDetails)

	println("Please wait loading the data.....")
	loadData()
	println("Data load is completed.....")

L:
	for true {

		displayOptions()
		println("Please Enter your option:")
		scanf("%d", &option)		 

		switch option {
		case 1:
			displayTags()
		case 2:
			search()
		case 3:
			break L
		default:
			log.Print("Invalid option")
		}
	}
}
 
// To load data into memory
func loadData() {
	loadImages()
	sortPredictDetails()	 
}


func loadImages() {

	type Image struct {
		URL string `json:"url"`
	}

	type Data struct {
		Images Image `json:"image"`
	}

	type Input struct {
		Datas Data `json:"data"`
	}

	type Request struct {
		Inputs []Input `json:"inputs"`
	}

	response, err := http.Get(IMAGES_URL);
	if err != nil {
		fmt.Printf("The HTTP request failed with error %s\n", err)
	}
	if err == nil {
		data, _ := ioutil.ReadAll(response.Body)

		fields := strings.Fields(string(data))

		length := len(fields)
		var startIndex, endIndex, offset = 0, 100, 100

		for startIndex < length {
		        var inputRequest Request
		        var inputs Input

			if endIndex > length-1 {
				endIndex = length - 1
			}

			println("loading data from image startIndex:", startIndex,", endIndex:" , endIndex,", TotalLength:" , length);

			var dataIndex int = 0
			// construct json data
			for index := startIndex; index <= endIndex; index++ {
				var image Image
				var data Data
				imageUrl := strings.TrimSpace(fields[index])
				image.URL = imageUrl
				data.Images = image
				inputs.Datas = data
				inputRequest.Inputs = append(inputRequest.Inputs, inputs)
				dataIndex++
			}

			jsonRequest, err := json.Marshal(inputRequest)
			if err != nil {
				fmt.Println(err)
				return
			}

			var jsonRequestString = string(jsonRequest) 
			pridictImages(jsonRequestString)
			startIndex = endIndex + 1
			endIndex += offset
		}

	}

}

func pridictImages(jsonRequestString string) {

	type InputImage struct {
		URL string `json:"url"`
	}

	type InputData struct {
		Image InputImage `json:"image"`
	}

	type RequestInput struct {
		Id   string    `json:"id,omitempty"`
		Data InputData `json:"data,omitempty"`
	}

	type ResponseConcepts struct {
		Name  string  `json:"name,omitempty"`
		Value float32 `json:"value,omitempty"`
	}

	type ResponseData struct {
		Concepts []ResponseConcepts `json:"concepts,omitempty"`
	}

	type ResponseOutput struct {
		Input RequestInput `json:"input,omitempty"`
		Data  ResponseData `json:"data,omitempty"`
	}

	type Response struct {
		Outputs []ResponseOutput `json:"outputs,omitempty"`
	}

	var jsonStr = []byte(jsonRequestString)

	req, err := http.NewRequest("POST", CLARIFAI_PREDICT_API_URL, bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", API_KEY)
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("X-Clarifai-REST-API-Key", "API_KEY")

	client := &http.Client{}
	resp, err := client.Do(req)

	if err != nil {
		println(err)
	}

	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

        
	response := Response{}
	jsonErr := json.Unmarshal(body, &response)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	if(len(response.Outputs) == 0) {
           println(string(body));
	}

	for _, responseOutput := range response.Outputs {

		imageUrl := responseOutput.Input.Data.Image.URL
		imageId := responseOutput.Input.Id
		imageIdAndImageMap[imageId] = imageUrl

		responseConcepts := responseOutput.Data.Concepts
		for conceptIndex := range responseConcepts {
		                        
			conceptName := strings.ToLower(responseConcepts[conceptIndex].Name);
			conceptValue := responseConcepts[conceptIndex].Value

			var imagePredictDetails ImagePredictDetails
			imagePredictDetails.image = imageUrl
			imagePredictDetails.value = conceptValue
			tagAndImagePredictDetails[conceptName] = append(tagAndImagePredictDetails[conceptName], imagePredictDetails)
		}

	}

}



func sortPredictDetails() {	 
	for _, predictDetails := range tagAndImagePredictDetails {
		sort.Slice(predictDetails[:], func(i, j int) bool {
			return predictDetails[i].value > predictDetails[j].value
		})

	}
}





func search() {

	println("Please enter the tag: ")

	var tagInput string
	scanf("%s\n", &tagInput)

	if len(strings.TrimSpace(tagInput)) == 0 {
		scanf("%s\n", &tagInput)
	}
	println("Entered tag:", tagInput)

	imagePredictDetails := tagAndImagePredictDetails[strings.ToLower(strings.TrimSpace(tagInput))];

	if imagePredictDetails == nil {
	        println("---------------------------------------------------------------------------------------------------------------------------");
                println("|                                           Search result not found.                                                       |");          
                println("---------------------------------------------------------------------------------------------------------------------------");            
	} else {

		endIndex := len(imagePredictDetails)
		if endIndex > 10 {
			endIndex = 10
		}
                 
                println("---------------------------------------------------------------------------------------------------------------------------");
                println("|                          Image                                                           |           value               |");          
                println("---------------------------------------------------------------------------------------------------------------------------");
		for index := 0; index < endIndex; index++ {
			result := imagePredictDetails[index];		 
		        fmt.Printf("|%-90s|%30f|\n", result.image, result.value);		 
		}
		println("----------------------------------------------------------------------------------------------------------------------------");
		
	}

}


func displayOptions() {
	println("1 --> Display tags")
	println("2 --> Search")
	println("3 --> Exit")
	println("----------------")
}

func displayTags() {

	if len(tagAndImagePredictDetails) == 0 {
		println("---------------------------------------------------------------------------------------------------------------------------")
		println("|                                           Tags not found.                                                               |")
		println("---------------------------------------------------------------------------------------------------------------------------")
	} else {
		println()
		print("[")
		for tag, _ := range tagAndImagePredictDetails {
			print(tag, ",")
		}
		print("]")
		println()
		println("--------------------------------------------------------------------------------------------------------------------------------------------")
		println()
	}
}


func displayImages() {

	println("---------------------------------------------------------Result----------------------")

	for imageId, image := range imageIdAndImageMap {
		println()
		println("	imageId =", imageId, "     : image ", image)

	}

	for tag, predictDetails := range tagAndImagePredictDetails {
		println()
		println("	tag =", tag, "  : predictDetails=", predictDetails)

	}

	println("--------------------------------------------------------End Result----------------------")
}
