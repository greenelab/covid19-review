# Review 1

The authors have proposed and realized an interesting framework to allow for the construction of a review in collaborative setting while ensuring high levels of traceability. The idea is quite fresh, and the technical implementation appropriate for the back-end. Given the pioneering character of their work, I do not necessarily see its limitations as reasons for rejection, but as points where their experiences and challenges might by themselves be useful for others. Many concern the front-end.

Regretfully, their live review https://greenelab.github.io/covid19-review/ could deter possible readers, as – at least within the first ~5 minutes – it did not render robustly on two different computers of mine after scrolling (tried one M1 mac, and one i7/64GB mac).

Further the linked repository https://github.com/greenelab/covid19-review/tree/e5a4e3ce43f493c0c913ae647951488b89345106/output did not contain manuscript.pdf which would have allowed for a possibly smooth read (or more specifically: the link in the readme file would point to a file that would not be publicly visible) ; I thus strongly recommend prior acceptance that https://greenelab.github.io/covid19-review/ will be extended to allow users a download of the composite pdf without any need to scroll or recompile (and wait seconds/minutes for text to appear when advancing the screen at https://greenelab.github.io/covid19-review).

The main contributors to the automated review seem to have been people that also contribute as authors to the current submission, or are otherwise affiliated with them. For others planning community efforts, it could be useful if the authors shared an extended discussion on where they faced obstacles - and success - in the recruitment of contributors, and how they see their mobilization efforts to compare to other groups which try to build and promote community around COVID-19 literature (e.g.: subdivision of preLights). Additionally, none of the most frequent contributors appear to include a medical doctor from pulmonary medicine – suggesting that some interesting potential community members have not been attracted.

Presently the user-interface for the construction of the review is provided by git/github. As the authors note, this could deter some contributors. Would there be ways to create a simple user interface that appeals to target contributors?

Reading the automated review, it seems to aggregate information, rather than to synthesize and condense the literature – which is a role of reviews that has been noted by others before (e.g.: in “Laboratory Life” by Latour and Woolgar). Therefore, it would be interesting to learn more about the author’s intended target audience and usage scenarios – and whether the work that they created would be even something new aside from “reviews” or “literature surveys”.

Though thinkable given their technical solution for the back-end, the option for personalized reviews appears absent in the discussion.

For their data-integration on clinical trials, they could possibly use the integration provided by dimensions.ai to save redundant work on their end.

# Review 2

This paper falls well into the scope of this workshop. It introduced a novel publishing platform, “Manubot,” which also acts as an infrastructure for collaboration and knowledge synthesis. In particular, it discussed the application of Manubot in producing a “living review” of covid-19, challenges that emerged with such a task, and how they dealt with the challenges. The paper is overall well written, and I only have a few minor suggestions.

(1) Section 2.1 didn’t give me a clear picture of the team structure that produces the review. What is the relation between recruited participants (“recruited by word of mouth and on Twitter”) and the consortium?

I am asking this also because, later on, you wrote: “We collaborated with the Immunology Institute at the Mount Sinai School of Medicine to incorporate summaries written by their students, post-docs, and faculty [49, 15]. Additionally, two of the consortium authors were undergraduate students recruited through the American Physician Scientist Association’s Virtual Summer Research Program.” It left me with the impression that there were two ways to recruit contributors. One is of relatively low barrier and informal (“recruited by word of mouth and on Twitter”). The other is of high barrier and formal (e.g., through organizations).

(2) Figure 3 has no associated narratives in the paper.

(3) It is not very clear to me how the knowledge synthesis and updating process take place. I only know how the summary statistics and figures were handled (“To address this concern, Manubot and GitHub’s CI features were used to create figures that integrated online data sources to respond to changes in the COVID-19 pandemic over time.”). How about the narratives?

(4) If you need more space to address the previous comments, I suggest the following to help you find some space.

    The spelling checking function (page 4-5) is not particularly interesting and doesn’t worth so much space.
    The emphasis that researchers in the biomedical domain are not particularly familiar with Git/GitHub. I understand it’s a major concern for the authors. Still, I don’t think this factor should take a front seat (e.g., mentioned at the very beginning of section 2.1) over other matters and be mentioned in several different places of the paper. I suggest pulling all materials about familiarizing users with GitHub into one section, including the concerns and solutions (e.g., training materials, easy tasks such as pull requests for beginners, using Gitter.im).

# Review 3

Summary
This paper addresses the COVID-19 infodemic by proposing a collaborative manuscript writing approach, using Manubot. Researchers from a variety of domains were asked to contribute to a review article that organizes the large quantity of COVID-19 related research. To this end, Manubot has been extended to add functionalities specifically needed for this use case.

General remarks
The paper is well written and relevant for this workshop, as it proposes a novel approach to collaborative sciences, in the form of version controlled living documents.

As the authors mention, the approach does require technical skills of researchers in order to contribute to a manuscript. Although instructions are provided, this is a major weakness of the approach. Although claimed differently by the authors, I do not think this approach will work for most researchers without the required technical skills. Even when they are willing to invest time in learning how to contribute to a manuscript, technical issues could arise and more complex git commands might be needed to solve this. What this paper is lacking, is a proper user evaluation that focuses on the question whether this approach is indeed suitable for non-technical users. For example, evaluating the usability of the whole process (e.g., with a SUS evaluation), and the participants’ attitudes towards the approach, !
or task load (via TLX assessment). At the current state, one cannot make claims on whether this approach is suitable for non-technical users.

In the introduction, the current challenges of scholarly communication (and in particular related to COVID-19 research) are listed. Although this paper does propose several solutions to mentioned issues (lacking collaboration, static review articles etc.), it does not directly address the most critical challenge: the "infodemic". The proposed approach still relies on document-based scholarly communication, and publications of the articles created with this approach will also contribute to the infodemic. A possible solution could be to integrate machine actionable descriptions of the results in the review articles, possibly by including semantic annotation to the text (I understand this might be out of scope for this research, but it is an interesting approach that would address the infodemic at its core).

Other remarks and questions

    A comparison with other manuscript authoring approaches and tools would be interesting. Why was Manubot selected in the first place? Are there any alternatives available that do not require technical skills, but still have support for versioning and collaborative authoring? How would this approach compare to using a Wiki system for authoring? Using Manubot was taken for granted without a justification.
    An itemized list of changes made to Manubot would be helpful (this is explained in the text already, but a list provides a better overview).
    The selection of participants could be biased towards people that are interested in technology already, otherwise they would not have participated in the first place. This should be mentioned as limitation.
    As mentioned in the paper, the manuscript grew too large for a single document. Why didn't the authors create multiple repositories for each of the articles?
    When does a contributor become an author of a paper? For example, fixing a typo is presumably not enough to be considered a paper author?
    Figure 5 does not seem to visualize the interests that are mention in the text and figure caption. Maybe the wrong figure is used here?
    Consider using footnotes for URLs.

