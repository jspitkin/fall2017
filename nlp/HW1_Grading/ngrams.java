import java.util.HashMap;
import java.util.HashSet;
import java.io.BufferedReader;
import java.io.FileReader;

public class ngrams 
{
	private static HashSet<String> uniqueUnigramStrings;

	private static HashMap<String, Integer> unigramFreq;
	private static HashMap<String, HashMap<String, Integer>> bigramFreq;

	private static double totalUnigrams;

	public static void main(String[] args)
	{
		if (args.length != 3 || !args[1].equals("-test"))
		{
			System.out.println("Usage: Java ngrams <training file> -test <test file>");
			return;
		}

		uniqueUnigramStrings = new HashSet<String>();
		unigramFreq = new HashMap<String, Integer> ();
		bigramFreq = new HashMap<String, HashMap<String, Integer>> ();


		totalUnigrams = 0;

		try (BufferedReader train_file = new BufferedReader(new FileReader(args[0])))
		{
			String in;
			while ((in = train_file.readLine()) != null)
			{
				//Assuming splitting on space is good enough, there's also whitespace regexes
				String[] unigrams = in.split(" ");

				String prevWord = "PHI";

				for (int i = 0; i < unigrams.length; i++)
				{
					String unigram = unigrams[i].toLowerCase();

					if (unigram.length() == 0)
						continue;
					
					uniqueUnigramStrings.add(unigram);

					if (unigramFreq.containsKey(unigram))
						unigramFreq.put(unigram, 1 + unigramFreq.get(unigram));
					else
						unigramFreq.put(unigram, 1);

					if (bigramFreq.containsKey(prevWord))
					{
						if (bigramFreq.get(prevWord).containsKey(unigram))
						{
							bigramFreq.get(prevWord).put(unigram, 1 + bigramFreq.get(prevWord).get(unigram));
						}
						else
						{
							bigramFreq.get(prevWord).put(unigram, 1);
						}
					}
					else
					{
						bigramFreq.put(prevWord, new HashMap<String, Integer> ());
						bigramFreq.get(prevWord).put(unigram, 1);
					}
					prevWord = unigram;
					totalUnigrams ++;
				}

			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
			return;
		}
		int uniqueUnigrams = uniqueUnigramStrings.size();

		String[] uniqueList = new String[uniqueUnigramStrings.size()];
		uniqueUnigramStrings.toArray(uniqueList);


		try (BufferedReader test_file = new BufferedReader(new FileReader(args[2])))
		{
			String in;
			while ((in = test_file.readLine()) != null)
			{
				double sentUni = 0;
				double sentBi = 0;
				double sentSmoothed = 0;

				boolean containsBigram = true;
				
				String[] unigrams = in.split(" ");

				String prevWord = "PHI";

				for (String unigram : unigrams)
				{
					unigram = unigram.toLowerCase();

          if (unigram.length() == 0)
            continue;

					sentUni += calcUnigramProb(unigram);
					double[] out = calcBigramProb(prevWord, unigram);
					if (out[0] == 1)
						containsBigram = false;
					else
						sentBi += out[0];
					sentSmoothed += out[1];

					prevWord = unigram;
				}

				System.out.println("S = " + in);
				System.out.println();

				System.out.printf("Unsmoothed Unigrams, logprob(S) = %.4f", sentUni);
				System.out.println();

				if (containsBigram)
					System.out.printf("Unsmoothed Bigrams, logprob(S) = %.4f", sentBi);
				else
					System.out.printf("Unsmoothed Bigrams, logprob(S) = undefined");
				System.out.println();

				System.out.printf("Smoothed Bigrams, logprob(S) = %.4f", sentSmoothed);
				System.out.println();
				System.out.println();


			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
			return;
		}

	}

	//First element is without smoothing, second is with
	private static double[] calcBigramProb(String first, String second)
	{
		double[] toReturn = new double[2];

		double bigramTotal = 0;


		if (bigramFreq.containsKey(first))
		{
			HashMap<String, Integer> secondSet = bigramFreq.get(first);

			for (String secondPoss : secondSet.keySet())
			{
				bigramTotal += secondSet.get(secondPoss);
			}
		}


		if (bigramFreq.containsKey(first) && bigramFreq.get(first).containsKey(second))
		{
			toReturn[0] = Math.log((bigramFreq.get(first).get(second)/bigramTotal))/Math.log(2);
		}
		else
			toReturn[0] = 1;

		double bigram = 0;
		if (bigramFreq.containsKey(first) && bigramFreq.get(first).containsKey(second))
			bigram = bigramFreq.get(first).get(second);
		toReturn[1] = Math.log((bigram + 1)/(bigramTotal + uniqueUnigramStrings.size()))/Math.log(2);
		//smoothedBigramProb.get(first).put(second, 0d);

		return toReturn;
	}

	private static double calcUnigramProb(String unigram)
	{
		return Math.log((unigramFreq.get(unigram)/totalUnigrams))/Math.log(2);
	}
}
