// NexusLead (Go) - buscador por terminal de empresas de cosmética en Núremberg
// usando el SDK oficial de OpenRegister (github.com/oregister/openregister-go).
//
// Uso:
//
//	export OPENREGISTER_API_KEY="tu_api_key"
//	go run . [-q texto] [-ciudad Nürnberg] [-wz] [-todas] [-p 1] [-n 20] [-csv leads.csv]
package main

import (
	"context"
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/oregister/openregister-go/v2"
)

// Palabras clave (en alemán) que se buscan en el objeto social registrado.
var keywordsCosmetica = []string{
	"Kosmetik", "kosmetisch", "Körperpflege", "Hautpflege", "Parfüm", "Duftstoffe", "Beauty",
}

// Códigos WZ 2025 relacionados con cosmética.
var wzCosmetica = []string{"20.42", "46.45", "47.75", "96.02"}

func main() {
	query := flag.String("q", "", "texto libre adicional (nombre, marca...)")
	ciudad := flag.String("ciudad", "Nürnberg", "ciudad")
	wz := flag.Bool("wz", false, "filtrar por códigos WZ de cosmética en vez de palabras clave")
	todas := flag.Bool("todas", false, "incluir también empresas inactivas")
	pagina := flag.Int64("p", 1, "página de resultados")
	porPagina := flag.Int64("n", 20, "resultados por página")
	csvPath := flag.String("csv", "", "exportar los resultados a CSV")
	flag.Parse()

	if os.Getenv("OPENREGISTER_API_KEY") == "" {
		fmt.Fprintln(os.Stderr, "Define la variable de entorno OPENREGISTER_API_KEY con tu API key.")
		os.Exit(1)
	}

	filters := []openregister.SearchFindCompaniesV1ParamsFilter{
		{Field: "city", SearchFilterBaseParam: openregister.SearchFilterBaseParam{Value: openregister.String(*ciudad)}},
	}
	if *wz {
		filters = append(filters, openregister.SearchFindCompaniesV1ParamsFilter{
			Field: "industry_codes", SearchFilterBaseParam: openregister.SearchFilterBaseParam{Values: wzCosmetica},
		})
	} else {
		filters = append(filters, openregister.SearchFindCompaniesV1ParamsFilter{
			Field: "purpose", SearchFilterBaseParam: openregister.SearchFilterBaseParam{Keywords: keywordsCosmetica},
		})
	}
	if !*todas {
		filters = append(filters, openregister.SearchFindCompaniesV1ParamsFilter{
			Field: "active", SearchFilterBaseParam: openregister.SearchFilterBaseParam{Value: openregister.String("true")},
		})
	}

	params := openregister.SearchFindCompaniesV1Params{
		Filters: filters,
		Pagination: openregister.SearchRequestPaginationParam{
			Page:    openregister.Int(*pagina),
			PerPage: openregister.Int(*porPagina),
		},
	}
	if *query != "" {
		params.Query = openregister.SearchFindCompaniesV1ParamsQuery{Value: *query}
	}

	client := openregister.NewClient() // lee OPENREGISTER_API_KEY del entorno
	res, err := client.Search.FindCompaniesV1(context.Background(), params)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error al consultar OpenRegister:", err)
		os.Exit(1)
	}

	p := res.Pagination
	fmt.Printf("\n%d empresas encontradas (página %d/%d)\n\n", p.TotalResults, p.Page, p.TotalPages)
	for i, e := range res.Results {
		activa := "no"
		if e.Active {
			activa = "sí"
		}
		fmt.Printf("%3d. %s  [%s, activa: %s]\n", i+1, e.Name, e.LegalForm, activa)
		if e.Address.FormattedValue != "" {
			fmt.Printf("     📍 %s\n", e.Address.FormattedValue)
		}
		fmt.Printf("     🏛  %s %s - %s  (%s)\n", e.RegisterType, e.RegisterNumber, e.RegisterCourt, e.CompanyID)
		if e.Purpose != "" {
			fmt.Printf("     📝 %s\n", recortar(strings.ReplaceAll(e.Purpose, "\n", " "), 160))
		}
		fmt.Println()
	}

	if *csvPath != "" {
		if err := guardarCSV(*csvPath, res.Results); err != nil {
			fmt.Fprintln(os.Stderr, "Error al guardar CSV:", err)
			os.Exit(1)
		}
		fmt.Printf("Guardadas %d empresas en %s\n", len(res.Results), *csvPath)
	}
}

func recortar(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n]) + "…"
}

func guardarCSV(ruta string, empresas []openregister.CompanySearchResponseItem) error {
	f, err := os.Create(ruta)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	w.Write([]string{"nombre", "forma_juridica", "activa", "direccion", "registro", "juzgado", "company_id", "objeto_social"})
	for _, e := range empresas {
		w.Write([]string{
			e.Name, string(e.LegalForm), fmt.Sprint(e.Active), e.Address.FormattedValue,
			strings.TrimSpace(string(e.RegisterType) + " " + e.RegisterNumber), e.RegisterCourt, e.CompanyID,
			strings.ReplaceAll(e.Purpose, "\n", " "),
		})
	}
	w.Flush()
	return w.Error()
}
